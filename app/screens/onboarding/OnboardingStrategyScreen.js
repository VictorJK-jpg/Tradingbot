import { useState } from "react";
import { View, Text, TouchableOpacity } from "react-native";
import { useNavigation } from "@react-navigation/native";

import api from "../../services/api";

const STRATEGIES = [
  { id: "dca", label: "DCA (Dollar Cost Average)", desc: "Regular fixed-amount purchases" },
  { id: "rsi_momentum", label: "RSI Momentum", desc: "Buy oversold, sell overbought" },
  { id: "macd_trend", label: "MACD Trend", desc: "Follow trend direction" },
  { id: "grid", label: "Grid Trading", desc: "Buy low, sell high in a range" },
  { id: "breakout", label: "Breakout", desc: "Enter on volume breakouts" },
  { id: "ai_advisory", label: "AI Advisory Only", desc: "No auto-trades, AI suggests only" },
];

export default function OnboardingStrategyScreen() {
  const navigation = useNavigation();
  const [selected, setSelected] = useState(["ai_advisory"]);
  const [loading, setLoading] = useState(false);

  const toggle = (id) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  };

  const handleNext = async () => {
    setLoading(true);
    try {
      await api.post("/onboarding/step-8", { selected_strategies: selected });
      navigation.navigate("OnboardingComplete");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View className="flex-1 bg-dark-900 px-6 pt-12">
      <Text className="text-brand-400 text-sm font-semibold mb-2">Step 8 of 9</Text>
      <Text className="text-white text-2xl font-bold mb-2">Strategy Selection</Text>
      <Text className="text-dark-600 mb-6">
        Pick strategies the AI can use. Advisory-only is the default.
      </Text>

      {STRATEGIES.map((s) => (
        <TouchableOpacity
          key={s.id}
          onPress={() => toggle(s.id)}
          className={`flex-row items-center justify-between px-4 py-3 rounded-xl mb-2 border ${
            selected.includes(s.id)
              ? "bg-brand-500/20 border-brand-500"
              : "bg-dark-800 border-dark-700"
          }`}
        >
          <View>
            <Text className="text-white font-semibold">{s.label}</Text>
            <Text className="text-dark-600 text-sm">{s.desc}</Text>
          </View>
          <View
            className={`w-6 h-6 rounded-full border items-center justify-center ${
              selected.includes(s.id) ? "bg-brand-500 border-brand-500" : "border-dark-600"
            }`}
          >
            {selected.includes(s.id) && <Text className="text-white text-xs">✓</Text>}
          </View>
        </TouchableOpacity>
      ))}

      <View className="flex-1" />
      <TouchableOpacity
        onPress={handleNext}
        disabled={loading || selected.length === 0}
        className={`py-4 rounded-xl items-center mb-6 ${
          selected.length > 0 && !loading ? "bg-brand-500" : "bg-dark-700"
        }`}
      >
        <Text className="text-white font-semibold text-lg">
          {loading ? "Saving..." : "Next"}
        </Text>
      </TouchableOpacity>
    </View>
  );
}
