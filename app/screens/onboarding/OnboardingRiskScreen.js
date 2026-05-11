import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity } from "react-native";
import { useNavigation } from "@react-navigation/native";

import api from "../../services/api";

const PRESETS = [
  {
    label: "Conservative",
    max_portfolio_risk_percent: 1,
    max_position_size_percent: 5,
    max_daily_loss_percent: 1,
    max_leverage: 1,
  },
  {
    label: "Moderate",
    max_portfolio_risk_percent: 2,
    max_position_size_percent: 10,
    max_daily_loss_percent: 3,
    max_leverage: 2,
  },
  {
    label: "Aggressive",
    max_portfolio_risk_percent: 5,
    max_position_size_percent: 20,
    max_daily_loss_percent: 5,
    max_leverage: 5,
  },
];

export default function OnboardingRiskScreen() {
  const navigation = useNavigation();
  const [config, setConfig] = useState(PRESETS[1]);
  const [tradingHoursStart, setTradingHoursStart] = useState("09:00");
  const [tradingHoursEnd, setTradingHoursEnd] = useState("17:00");
  const [maxDailyTrades, setMaxDailyTrades] = useState("5");
  const [loading, setLoading] = useState(false);

  const applyPreset = (preset) => setConfig({ ...preset });

  const handleNext = async () => {
    setLoading(true);
    try {
      await api.post("/onboarding/step-5", {
        ...config,
        trading_hours_start: tradingHoursStart,
        trading_hours_end: tradingHoursEnd,
        max_daily_trades: parseInt(maxDailyTrades, 10),
      });
      navigation.navigate("OnboardingAssets");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View className="flex-1 bg-dark-900 px-6 pt-12">
      <Text className="text-brand-400 text-sm font-semibold mb-2">Step 5 of 9</Text>
      <Text className="text-white text-2xl font-bold mb-2">Risk Profile</Text>
      <Text className="text-dark-600 mb-6">
        Hard limits the AI will never exceed. Choose a preset or customise.
      </Text>

      {/* Presets */}
      <View className="flex-row gap-2 mb-6">
        {PRESETS.map((p) => (
          <TouchableOpacity
            key={p.label}
            onPress={() => applyPreset(p)}
            className={`flex-1 py-2 rounded-xl items-center border ${
              config.label === p.label
                ? "bg-brand-500 border-brand-500"
                : "bg-dark-800 border-dark-700"
            }`}
          >
            <Text
              className={`font-semibold ${
                config.label === p.label ? "text-white" : "text-dark-600"
              }`}
            >
              {p.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Risk Fields */}
      {[
        { key: "max_portfolio_risk_percent", label: "Max Risk per Trade (%)" },
        { key: "max_position_size_percent", label: "Max Position Size (%)" },
        { key: "max_daily_loss_percent", label: "Max Daily Loss (%)" },
        { key: "max_leverage", label: "Max Leverage" },
      ].map((field) => (
        <View key={field.key} className="mb-3">
          <Text className="text-white font-semibold mb-1">{field.label}</Text>
          <TextInput
            className="bg-dark-800 text-white px-4 py-2 rounded-xl border border-dark-700"
            keyboardType="numeric"
            value={String(config[field.key])}
            onChangeText={(t) =>
              setConfig((prev) => ({ ...prev, [field.key]: parseFloat(t) || 0 }))
            }
          />
        </View>
      ))}

      <Text className="text-white font-semibold mb-2 mt-2">Trading Hours</Text>
      <View className="flex-row gap-2 mb-3">
        <TextInput
          className="flex-1 bg-dark-800 text-white px-4 py-2 rounded-xl border border-dark-700"
          placeholder="09:00"
          value={tradingHoursStart}
          onChangeText={setTradingHoursStart}
        />
        <TextInput
          className="flex-1 bg-dark-800 text-white px-4 py-2 rounded-xl border border-dark-700"
          placeholder="17:00"
          value={tradingHoursEnd}
          onChangeText={setTradingHoursEnd}
        />
      </View>

      <View className="mb-6">
        <Text className="text-white font-semibold mb-1">Max Daily Trades</Text>
        <TextInput
          className="bg-dark-800 text-white px-4 py-2 rounded-xl border border-dark-700"
          keyboardType="numeric"
          value={maxDailyTrades}
          onChangeText={setMaxDailyTrades}
        />
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
