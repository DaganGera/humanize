import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import humanize  # noqa: E402
import latex_text  # noqa: E402
import stylo  # noqa: E402

CLI = [sys.executable, os.path.join(ROOT, "scripts", "humanize.py")]

MACHINE = (
    "Soil health is a crucial foundation of sustainable agriculture. This study addresses a key gap, "
    "highlighting the role of enzymes rather than chemistry alone. Together, these findings offer a "
    "robust, comprehensive and practical framework. The approach remains effective across diverse "
    "settings, underscoring its broader value. "
) * 6

HUMAN = (
    "The activity of dehydrogenases was measured in 36 soil samples taken from two layers (0-20 cm and "
    "20-40 cm) at six points of the field. In the top layer the activity ranged from 0.092 to 0.164 mg "
    "(mean 0.127), which was higher than in the 20-40 cm layer (mean 0.106). There is a similar "
    "difference in the data of Smith et al. [C], who sampled 12 fields in Poland in 2015. However, the "
    "highest activity was found at point 2, and this may be related to the organic carbon content "
    "(Table 4). It was not possible to repeat the measurement in 2019. "
) * 6


def write(text, suffix):
    f = tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8")
    f.write(text)
    f.close()
    return f.name


class Features(unittest.TestCase):
    def test_sentence_split_keeps_abbreviations(self):
        s = stylo.split_sentences("We used the method of Lee et al. in two steps (i.e. train and test). It worked.")
        self.assertEqual(len(s), 2)

    def test_machine_text_is_less_anchored(self):
        m, h = stylo.features(MACHINE), stylo.features(HUMAN)
        self.assertLess(m["anchor_share"], h["anchor_share"])
        self.assertGreater(m["promo"], h["promo"])
        self.assertGreater(m["part_tail"], h["part_tail"])
        self.assertLess(m["numerals"], h["numerals"])

    def test_short_text_returns_nothing(self):
        self.assertEqual(stylo.features("Too short."), {})


class Latex(unittest.TestCase):
    TEX = (
        "\\documentclass{article}\n\\begin{document}\n\\section{Introduction}\n"
        "Buildings are hard to segment \\citep{a2020} and the error is $x^2$ in most of the cases that we looked at here.\n\n"
        "\\begin{equation}\ny = 2\n\\end{equation}\n\n\\section{Methods}\n"
        "We trained the model for 100 epochs on the data of Section~\\ref{sec:data} with a batch size of 8 images.\n"
        "\\end{document}\n"
    )

    def test_sections_and_markers(self):
        ps = latex_text.paragraphs(self.TEX)
        self.assertEqual([p["section"] for p in ps], ["Introduction", "Methods"])
        self.assertIn("[C]", ps[0]["text"])
        self.assertIn("[M]", ps[0]["text"])
        self.assertNotIn("\\", ps[1]["text"])
        self.assertEqual(ps[0]["line"], 4)


class Cli(unittest.TestCase):
    def test_measure_flags_machine_text(self):
        out = subprocess.run(CLI + ["measure", write(MACHINE, ".txt"), "--section", "discussion", "--json"],
                             capture_output=True, text=True, check=True).stdout
        flagged = {g["feature"] for g in json.loads(out)[0]["gaps"]}
        self.assertTrue({"promo", "part_tail"} & flagged, flagged)

    def test_measure_passes_human_text(self):
        out = subprocess.run(CLI + ["measure", write(HUMAN, ".txt"), "--section", "results", "--json"],
                             capture_output=True, text=True, check=True).stdout
        flagged = {g["feature"] for g in json.loads(out)[0]["gaps"]}
        self.assertFalse({"promo", "part_tail", "rather_than", "anchor_share"} & flagged, flagged)

    def test_check_catches_changed_number_and_lost_citation(self):
        a = write("\\begin{document}\nThe IoU was 0.94 \\citep{lee2020} on the test set of 120 images in total.\n\\end{document}\n", ".tex")
        b = write("\\begin{document}\nThe IoU was 0.95 on the test set of 120 images in total, as reported.\n\\end{document}\n", ".tex")
        r = subprocess.run(CLI + ["check", a, b], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("0.94", r.stdout)
        self.assertIn("lee2020", r.stdout)
        self.assertEqual(subprocess.run(CLI + ["check", a, a], capture_output=True, text=True).returncode, 0)

    def test_baseline_from_own_text(self):
        out = write("", ".json")
        own = "\n\n".join([HUMAN[: len(HUMAN) // 6]] * 12)
        subprocess.run(CLI + ["baseline", write(own, ".txt"), "-o", out, "--chunk", "80"],
                       capture_output=True, text=True, check=True)
        with open(out) as f:
            self.assertIn("sent_len_mean", json.load(f)["sections"]["all"])

    def test_markdown_skips_code(self):
        md = "# Title\n\nThis paragraph has enough words in it to be counted by the reader as prose text.\n\n```\nrm -rf nothing here 123\n```\n"
        units = humanize.read_units(write(md, ".md"))
        self.assertEqual(len(units), 1)
        self.assertNotIn("rm -rf", units[0][1][0][1])


class Data(unittest.TestCase):
    def test_baselines_cover_profiles(self):
        with open(os.path.join(ROOT, "data", "baselines.json")) as f:
            b = json.load(f)
        for sec in ("intro", "methods", "results", "discussion", "conclusion"):
            self.assertIn("anchor_share", b["profiles"]["research-paper"][sec])
        for prof in ("blog-essay", "book-fiction", "book-nonfiction", "conversation"):
            self.assertIn(b["aliases"][prof], b["profiles"])

    def test_every_profile_file_exists(self):
        with open(os.path.join(ROOT, "SKILL.md"), encoding="utf-8") as f:
            skill = f.read()
        import re
        for f in re.findall(r"`(profiles/[\w-]+\.md)`", skill):
            self.assertTrue(os.path.exists(os.path.join(ROOT, f)), f)

    def test_lexicon_entries_are_dated(self):
        with open(os.path.join(ROOT, "data", "lexicon.json")) as f:
            d = json.load(f)
        self.assertTrue(all(e["era"] and e["source"] and e["phrases"] for e in d["entries"]))


if __name__ == "__main__":
    unittest.main()
