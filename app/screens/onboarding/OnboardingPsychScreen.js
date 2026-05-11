import { useState } from "react";
import { View, Text, TouchableOpacity } from "react-native";
import { useNavigation } from "@react-navigation/native";

import api from "../../services/api";

const TRAITS = [
  { key: "fomo_score", label: "FOMO", low: "Patient", high: "Impulsive" },
  { key: "panic_score", label: "Panic Selling", low: "Steady", high: "Reactive" },
  { key: "overtrading_score", label: "Overtrading", low: "Disciplined", high: "Frequent" },
  { key: "revenge_trading_score", label: "Revenge Trading", low: "Calm", high: "Aggressive" },
  { key: "holding_too_long_score", label: "Holding Too Long", low: "Flexible", high: "Stubborn" },
];

export default function OnboardingPsychScreen() {
  const navigation = useNavigation();
  const [scores, setScores] = useState(
    Object.fromEntries(TRAITS.map((t) => [t.key, 50]))
  );
  const [coolingOff, setCoolingOff] = useState(false);
  const [loading, setLoading] = useState(false);

  const updateScore = (key, delta) => {
    setScores((prev) => ({
      ...prev,
      [key]: Math.max(0, Math.min(100, prev[key] + delta)),
    }));
  };

  const handleNext = async () => {
    setLoading(true);
    try {
      await api.post("/onboarding/step-3", {
        ...scores,
        cooling_off_enabled: coolingOff,
        cooling_off_minutes: 30,
      });
      navigation.navigate("OnboardingGoals");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View className="flex-1 bg-dark-900 px-6 pt-12">
      <Text className="text-brand-400 text-sm font-semibold mb-2">Step 3 of 9</Text>
      <Text className="text-white text-2xl font-bold mb-2">Psychological Profile</Text>
      <Text className="text-dark-600 mb-6">
        Be honest — the AI uses this to protect you from yourself.
      </Text>

      {TRAITS.map((trait) => (
        <View key={trait.key} className="mb-4">
          <View className="flex-row justify-between mb-2">
            <Text className="text-white font-semibold">{trait.label}</Text>
            <Text className="text-brand-400 font-bold">{scores[trait.key]}</Text>
          </View>
          <View className="flex-row items-center">
            <TouchableOpacity
              onPress={() => updateScore(trait.key, -10)}
              className="w-8 h-8 bg-dark-800 rounded-full items-center justify-center border border-dark-700"
            >
              <Text className="text-white">-</Text>
            </TouchableOpacity>
            <View className="flex-1 h-2 bg-dark-800 rounded-full mx-3 overflow-hidden">
              <View
                className="h-full bg-brand-500 rounded-full"
                style={{ width: `${scores[trait.key]}%` }}
              />
            </View>
            <TouchableOpacity
              onPress={() => updateScore(trait.key, 10)}
              className="w-8 h-8 bg-dark-800 rounded-full items-center justify-center border border-dark-700"
            >
              <Text className="text-white">+</Text>
            </TouchableOpacity>
          </View>
          <View className="flex-row justify-between mt-1">
            <Text className="text-dark-600 text-xs">{trait.low}</Text>
            <Text className="text-dark-600 text-xs">{trait.high}</Text>
          </View>
        </View>
      ))}

      <View className="flex-row items-center mt-4 mb-6">
        <TouchableOpacity
          onPress={() => setCoolingOff(!coolingOff)}
          className={`w-6 h-6 rounded border mr-3 items-center justify-center ${
            coolingOff ? "bg-brand-500 border-brand-500" : "bg-dark-800 border-dark-600"
          }`}
        >
          {coolingOff && <Text className="text-white text-xs">✓</Text>}
        </TouchableOpacity>
        <Text className="text-white">Enable cooling-off period after losses</Text>
      </View>

      <View className="flex-1" />
      <TouchableOpacity
        onPress={handleNext}
        disabled={loading}
        className="bg-brand-500 py-4 rounded-xl items-center mb-6"
      >
        <Text className="text-white font-semibold text-lg">
          {loading ? "Saving..." : "Next"}
        </Text>
      </TouchableOpacity>
    </View>
  );
}
