import unittest
from resources.lib.subtitle.srt_subtitle_creator import SrtSubtitleCreator
from resources.lib.subtitle.sub_subtitle_creator import SubSubtitleCreator
from resources.lib.subtitle.create_classical_times import create_classical_times
from resources.lib.subtitle.subtitle import Subtitle
from resources.lib.subtitle.subtitleline import SubtitleLine

class TestCases(unittest.TestCase):
    def mock_srt(self):
        return ["1", 
                "01:12:16,639 --> 01:12:19,057", 
                '<font color="#FFFFFF">SampleText1</font>\n', "SampleText2\n", "", 
                "2",
                "01:15:19,058 --> 01:15:21,226",
                "SampleText1   ", "SampleText2  ", "", "", ""]  

    def mock_srt_other(self):
        return ["1", 
                "00:12:16,639 --> 00:12:19,057", 
                '<font color="#FFFFFF">SampleText1</font>\n', "SampleText2\n", "", 
                "2",
                "02:15:19,058 --> 02:15:21,226",
                "SampleText1   ", "SampleText2  ", "", "", ""]  

    def mock_sub(self):
        return ['{2133}{34244}SampleText1|SampleText2', "{32423}{34234}SampleText1  |SampleText3   "]

    def test_srt_subtitlecreator_success(self):
        subtitlecreator = SrtSubtitleCreator(self.mock_srt())
        subtitlecreator.load_subtitle()
        self.assertEqual(len(subtitlecreator.subtitlelines), 2)
        self.assertIsInstance(subtitlecreator.subtitlelines[0], SubtitleLine)

    def test_srt_subtitlecreator_fail(self):
        subtitlefile = SrtSubtitleCreator(["A", "B", "C"])
        self.assertRaises(TypeError, subtitlefile.load_subtitle)

    def test_srt_subtitlecreator_times(self):
        subtitlecreator = SrtSubtitleCreator(self.mock_srt())
        subtitlecreator.load_subtitle()
        subtitle = subtitlecreator.subtitlelines[0]
        self.assertEqual(4336639, subtitle.startingtime)
        self.assertEqual(4339057, subtitle.endingtime)

    def test_srt_subtitlecreator_text_creation(self):
        subtitlecreator = SrtSubtitleCreator(self.mock_srt())
        subtitlecreator.load_subtitle()
        subtitle = subtitlecreator.subtitlelines[1]
        self.assertEqual(subtitle.textlines, ["SampleText1", "SampleText2"])            
        self.assertEqual(subtitle.text(), "SampleText1\nSampleText2")     

    def test_sub_subtitlecreator_success(self):
        subtitlecreator = SubSubtitleCreator(self.mock_sub(), 25)
        subtitlecreator.load_subtitle()
        self.assertEqual(len(subtitlecreator.subtitlelines), 2)
        self.assertIsInstance(subtitlecreator.subtitlelines[0], SubtitleLine)

    def test_sub_subtitlecreator_fail(self):
        subtitlecreator = SubSubtitleCreator(self.mock_srt(), 25)
        self.assertRaises(TypeError, subtitlecreator.load_subtitle)
 
    def test_sub_subtitlecreator_times(self):
        subtitlecreator = SubSubtitleCreator(self.mock_sub(), 25)
        subtitlecreator.load_subtitle()
        subtitle = subtitlecreator.subtitlelines[0]
        self.assertEqual(85320.0, subtitle.startingtime)
        self.assertEqual(1369760.0, subtitle.endingtime)

    def test_sub_subtitlecreator_text_creation(self):
        subtitlecreator = SubSubtitleCreator(self.mock_sub(), 25)
        subtitlecreator.load_subtitle()
        subtitle = subtitlecreator.subtitlelines[1]
        self.assertEqual(subtitle.textlines, ["SampleText1", "SampleText3"])            
        self.assertEqual(subtitle.text(), "SampleText1\nSampleText3")    

    def mock_subtitle(self, subtitlefile=None):
        if not subtitlefile:
            subtitlefile = self.mock_srt()
        subtitlecreator = SrtSubtitleCreator(subtitlefile)
        subtitlecreator.load_subtitle()
        return Subtitle("mock_filename", subtitlecreator.subtitlelines, "utf-8", None)

    def test_seach_in_subtitle(self):
        subtitle = self.mock_subtitle()
        aa = subtitle.search_in_subtitle("SampleText1")
        self.assertIsInstance(aa[0], SubtitleLine)
        self.assertEqual(len(aa), 2)

    def test_html_color_change(self):
        subtitle = self.mock_subtitle()
        subtitle.change_html_color("00FF00")
        self.assertIn("00FF00", str(subtitle))

    def test_sync_to_chosen_times(self):
        subtitle = self.mock_subtitle()
        subtitle.sync_chosen_lines_to_chosen_times(1000, 100000, 0, 1)
        self.assertEqual(subtitle[0].startingtime, 1000.0)
        self.assertEqual(subtitle[1].startingtime, 100000.0)

    def test_sync_two_subtitle(self):
        subtitle = self.mock_subtitle()
        subtitle2 = self.mock_subtitle(self.mock_srt_other())
        subtitle.sync_two_subtitles(subtitle2, 0, -1, 0, -1)
        self.assertEqual(subtitle[0].startingtime, subtitle2[0].startingtime)
        self.assertEqual(subtitle[1].startingtime, subtitle2[1].startingtime)

    def test_deletion(self):
        subtitle = self.mock_subtitle()
        del subtitle[0]
        self.assertTrue(subtitle.changed)
        self.assertEqual(len(subtitle), 1)

    def test_easy_list(self):
        subtitle = self.mock_subtitle()
        subtitle_per_line, lines = subtitle.easy_list_selector()
        self.assertEqual(lines, [0,0,0,0,0,1,1,1,1,1])

    def test_time_conversion(self):
        subtitle = self.mock_subtitle()
        test_time = 346212
        classical_time = create_classical_times(test_time)
        self.assertEqual(test_time, subtitle.create_decimal_times(classical_time))    

    def test_time_conversion_reverse(self):
        subtitle = self.mock_subtitle()
        test_time = "01:33:23,332"
        decimal_time = subtitle.create_decimal_times(test_time)
        self.assertEqual(test_time, create_classical_times(decimal_time))   

    def test_change_text(self):
        subtitle = self.mock_subtitle()
        subtitle.change_text(0, "newtext1\nnewtext2")
        self.assertEqual(subtitle[0].textlines, ["newtext1", "newtext2"])
        self.assertTrue(subtitle.changed)

    def test_shift_forwards(self):
        subtitle = self.mock_subtitle()
        old_start = subtitle[0].startingtime
        subtitle.shift_subtitle(10000)
        self.assertEqual(subtitle[0].startingtime, old_start+10000)
        self.assertTrue(subtitle.changed)

    def test_shift_backwards(self):
        subtitle = self.mock_subtitle()
        old_start = subtitle[0].startingtime
        subtitle.shift_subtitle(-10000)
        self.assertEqual(subtitle[0].startingtime, old_start-10000)
        self.assertTrue(subtitle.changed)

    def test_stretch_subtitle(self):
        subtitle = self.mock_subtitle()
        old_start = subtitle[0].startingtime
        subtitle.stretch_subtitle(1.2)
        self.assertEqual(old_start*1.2, subtitle[0].startingtime)

    def test_shrink_subtitle(self):
        subtitle = self.mock_subtitle()
        old_start = subtitle[0].startingtime
        subtitle.stretch_subtitle(0.8)
        self.assertEqual(old_start*0.8, subtitle[0].startingtime)

    def test_stretch_subtitle_correction(self):
        subtitle = self.mock_subtitle()
        old_start = subtitle[0].startingtime
        subtitle.stretch_subtitle(1.2, 1000)
        self.assertEqual(old_start*1.2-1000, subtitle[0].startingtime)

    def test_stretch_to_new_end(self):
        subtitle = self.mock_subtitle()
        old_start = subtitle[-1].startingtime
        new_end = 500000.0
        subtitle.stretch_to_new_end(new_end)
        self.assertEqual(subtitle[-1].startingtime, new_end)

    def test_shrink_to_new_end(self):
        subtitle = self.mock_subtitle()
        new_end = 5000.0
        subtitle.stretch_to_new_end(new_end)
        self.assertEqual(subtitle[-1].startingtime, new_end)

    def test_shift_to_new_start(self):
        subtitle = self.mock_subtitle()
        new_start = 10000
        subtitle.shift_to_new_start(new_start)
        self.assertEqual(new_start, subtitle[0].startingtime)

    def test_sync_to_new_times(self):
        subtitle = self.mock_subtitle()
        subtitle.sync_to_times("00:10:10:100", "01:20:20:100")
        self.assertAlmostEqual(subtitle[0].startingtime, 610100.0)
        self.assertAlmostEqual(subtitle[-1].startingtime, 4820100.0)

if __name__ == '__main__':
    unittest.main()    
