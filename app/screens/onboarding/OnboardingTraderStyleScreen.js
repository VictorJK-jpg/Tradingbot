import { useState } from "react";
import { View, Text, TouchableOpacity } from "react-native";
import { useNavigation } from "@react-navigation/native";

import api from "../../services/api";

const STYLES = [
  { id: "scalper", label: "Scalper", desc: "Minutes to hours" },
  { id: "day_trader", label: "Day Trader", desc: "Intraday only" },
  { id: "swing_trader", label: "Swing Trader", desc: "Days to weeks" },
  { id: "position_trader", label: "Position Trader", desc: "Weeks to months" },
  { id: "investor", label: "Investor", desc: "Months to years" },
];

const EXPERIENCE = [
  { id: "beginner", label: "Beginner" },
  { id: "intermediate", label: "Intermediate" },
  { id: "advanced", label: "Advanced" },
  { id: "expert", label: "Expert" },
];

export default function OnboardingTraderStyleScreen() {
  const navigation = useNavigation();
  const [style, setStyle] = useState("");
  const [experience, setExperience] = useState("");
  const [loading, setLoading] = useState(false);

  const handleNext = async () => {
    if (!style || !experience) return;
    setLoading(true);
    try {
      await api.post("/onboarding/step-2", { style, experience });
      navigation.navigate("OnboardingPsych");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View className="flex-1 bg-dark-900 px-6 pt-12">
      <Text className="text-brand-400 text-sm font-semibold mb-2">Step 2 of 9</Text>
      <Text className="text-white text-2xl font-bold mb-2">Trading Style</Text>
      <Text className="text-dark-600 mb-6">How do you trade?</Text>

      <Text className="text-white font-semibold mb-3">Style</Text>
      {STYLES.map((s) => (
        <TouchableOpacity
          key={s.id}
          onPress={() => setStyle(s.id)}
          className={`flex-row items-center justify-between px-4 py-3 rounded-xl mb-2 border ${
            style === s.id
              ? "bg-brand-500/20 border-brand-500"
              : "bg-dark-800 border-dark-700"
          }`}
        >
          <Text className="text-white font-semibold">{s.label}</Text>
          <Text className="text-dark-600 text-sm">{s.desc}</Text>
        </TouchableOpacity>
      ))}

      <Text className="text-white font-semibold mb-3 mt-4">Experience</Text>
      <View className="flex-row flex-wrap gap-2">
        {EXPERIENCE.map((e) => (
          <TouchableOpacity
            key={e.id}
            onPress={() => setExperience(e.id)}
            className={`px-4 py-2 rounded-xl border ${
              experience === e.id
                ? "bg-brand-500 border-brand-500"
                : "bg-dark-800 border-dark-700"
            }`}
          >
            <Text
              className={`font-semibold ${
                experience === e.id ? "text-white" : "text-dark-600"
              }`}
            >
              {e.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <View className="flex-1" />
      <TouchableOpacity
        onPress={handleNext}
        disabled={!style || !experience || loading}
        className={`py-4 rounded-xl items-center mb-6 ${
          style && experience && !loading ? "bg-brand-500" : "bg-dark-700"
        }`}
      >
        <Text className="text-white font-semibold text-lg">
          {loading ? "Saving..." : "Next"}
        </Text>
      </TouchableOpacity>
    </View>
  );
}
