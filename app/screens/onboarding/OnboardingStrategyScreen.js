import React, { useState } from "react";
import { View, Text, TouchableOpacity, ScrollView } from "react-native";
import { useNavigation } from "@react-navigation/native";

import api from "../../services/api";

const COLORS = {
  white: "#F9F9F7",
  black: "#111111",
  gray: "#E5E5E0",
  red: "#CC0000",
  midGray: "#737373",
};

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
    <View style={{ flex: 1, backgroundColor: COLORS.white }}>
      <View style={{ paddingTop: 60, paddingHorizontal: 16, borderBottomWidth: 4, borderBottomColor: COLORS.black, paddingBottom: 12 }}>
        <Text style={{ color: COLORS.midGray, fontSize: 11, textTransform: "uppercase" }}>Step 8 of 9</Text>
        <Text style={{ color: COLORS.black, fontSize: 28, fontWeight: "bold", fontFamily: "Times New Roman" }}>STRATEGY SELECTION</Text>
      </View>
      
      <Text style={{ color: COLORS.midGray, fontSize: 13, paddingHorizontal: 16, paddingTop: 16, paddingBottom: 20, borderBottomWidth: 1, borderBottomColor: COLORS.gray }}>
        Pick strategies the AI can use. Advisory-only is the default.
      </Text>

      <ScrollView style={{ flex: 1, paddingHorizontal: 16 }}>
        {STRATEGIES.map((s) => (
          <TouchableOpacity
            key={s.id}
            onPress={() => toggle(s.id)}
            style={{
              flexDirection: "row",
              justifyContent: "space-between",
              alignItems: "center",
              padding: 16,
              marginTop: 12,
              borderWidth: 1,
              borderColor: selected.includes(s.id) ? COLORS.black : COLORS.gray,
              backgroundColor: selected.includes(s.id) ? COLORS.black : COLORS.white,
            }}
          >
            <View>
              <Text style={{ color: selected.includes(s.id) ? COLORS.white : COLORS.black, fontWeight: "bold", fontSize: 14, textTransform: "uppercase" }}>{s.label}</Text>
              <Text style={{ color: selected.includes(s.id) ? COLORS.gray : COLORS.midGray, fontSize: 12, marginTop: 4 }}>{s.desc}</Text>
            </View>
            <View style={{
              width: 24,
              height: 24,
              borderWidth: 2,
              borderColor: selected.includes(s.id) ? COLORS.white : COLORS.black,
              alignItems: "center",
              justifyContent: "center",
            }}>
              {selected.includes(s.id) && <Text style={{ color: COLORS.white, fontSize: 14, fontWeight: "bold" }}>✓</Text>}
            </View>
          </TouchableOpacity>
        ))}
      </ScrollView>
      
      <View style={{ padding: 16, borderTopWidth: 4, borderTopColor: COLORS.black }}>
        <TouchableOpacity
          onPress={handleNext}
          disabled={loading || selected.length === 0}
          style={{
            backgroundColor: selected.length > 0 && !loading ? COLORS.black : COLORS.gray,
            paddingVertical: 16,
            borderWidth: 1,
            borderColor: selected.length > 0 && !loading ? COLORS.black : COLORS.midGray,
          }}
        >
          <Text style={{ color: COLORS.white, textAlign: "center", fontWeight: "bold", fontSize: 14, textTransform: "uppercase", letterSpacing: 2 }}>
            {loading ? "Saving..." : "Next"}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}
