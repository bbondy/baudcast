"""Tests for signal generation."""

from __future__ import annotations

import unittest

from warble.config import DEFAULT_CONFIG
from warble.demodulator import goertzel_magnitude
from warble.modulator import bits_to_samples, generate_tone


class ModulatorTests(unittest.TestCase):
    def test_generate_tone_uses_symbol_length(self) -> None:
        tone = generate_tone(DEFAULT_CONFIG.freq0)
        self.assertEqual(len(tone), DEFAULT_CONFIG.samples_per_symbol)

    def test_bits_to_samples_concatenates_symbols(self) -> None:
        bits = [0, 1, 1, 0]
        samples = bits_to_samples(bits)
        self.assertEqual(len(samples), len(bits) * DEFAULT_CONFIG.samples_per_symbol)

    def test_generated_tone_has_more_energy_at_target_frequency(self) -> None:
        tone = generate_tone(DEFAULT_CONFIG.freq1)
        low = goertzel_magnitude(tone, DEFAULT_CONFIG.freq0, DEFAULT_CONFIG.sample_rate)
        high = goertzel_magnitude(tone, DEFAULT_CONFIG.freq1, DEFAULT_CONFIG.sample_rate)
        self.assertGreater(high, low)


if __name__ == "__main__":
    unittest.main()
