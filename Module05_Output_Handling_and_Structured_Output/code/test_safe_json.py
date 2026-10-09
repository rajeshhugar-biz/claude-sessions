"""Unit tests for safe_json.extract_json. Run: python -m unittest -v"""
import unittest
from safe_json import extract_json


class ExtractJsonTests(unittest.TestCase):
    def test_clean_object(self):
        self.assertEqual(extract_json('{"a": 1}'), {"a": 1})

    def test_json_fence(self):
        self.assertEqual(extract_json('```json\n{"a": 1}\n```'), {"a": 1})

    def test_fence_without_language_and_uppercase(self):
        self.assertEqual(extract_json('```\n{"a": 1}\n```'), {"a": 1})
        self.assertEqual(extract_json('```JSON\n{"a": 1}\n```'), {"a": 1})

    def test_prose_before_and_after(self):
        text = 'Here is the result:\n{"a": {"b": [1, 2]}}\nHope this helps!'
        self.assertEqual(extract_json(text), {"a": {"b": [1, 2]}})

    def test_prose_around_fence(self):
        text = 'Sure.\n```json\n{"a": 1}\n```\nAnything else?'
        self.assertEqual(extract_json(text), {"a": 1})

    def test_byte_order_mark_and_whitespace(self):
        self.assertEqual(extract_json('\ufeff  \n {"a": 1}  '), {"a": 1})

    def test_braces_inside_strings(self):
        self.assertEqual(extract_json('{"s": "a } b { c"}'), {"s": "a } b { c"})

    def test_first_of_two_objects(self):
        self.assertEqual(extract_json('{"a": 1}\n{"a": 2}'), {"a": 1})

    def test_unicode_values(self):
        self.assertEqual(extract_json('{"city": "Pune", "sym": "₹"}')["sym"],
                         "₹")

    def test_list_mode(self):
        self.assertEqual(extract_json("Items: [1, 2, 3].", want=list), [1, 2, 3])

    def test_truncated_raises(self):
        with self.assertRaises(ValueError):
            extract_json('{"a": 1, "items": [{"b": 2}, {"c"')

    def test_truncated_does_not_return_inner_object(self):
        with self.assertRaises(ValueError):  # must not silently return {"b": 2}
            extract_json('{"a": {"b": 2}, "c": [')

    def test_empty_and_none_raise(self):
        for bad in ("", "   ", None):
            with self.assertRaises(ValueError):
                extract_json(bad)

    def test_no_json_raises(self):
        with self.assertRaises(ValueError):
            extract_json("Sorry, I cannot help with that.")

    def test_nan_rejected(self):
        with self.assertRaises(ValueError):
            extract_json('{"total": NaN}')


if __name__ == "__main__":
    unittest.main()
