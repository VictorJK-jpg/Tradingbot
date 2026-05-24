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

const STYLES = [
  { id: "scalper", label: "Scalper", desc: "Minutes to hours" },
  { id: "day_trader", label: "Day Trader", desc: "Intraday only" },
  { id: "swing_trader", label: "Swing Trader", desc: "Days to weeks" },
  { id: "position_trader", label: "Position Trader", desc: "Weeks to months" },
  { id: "investor", label: "Investor", desc: "Months to years" },
];

const EXPERIENCE = [
  { id: "beginner", label: "BEGINNER" },
  { id: "intermediate", label: "INTERMEDIATE" },
  { id: "advanced", label: "ADVANCED" },
  { id: "expert", label: "EXPERT" },
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
    <View style={{ flex: 1, backgroundColor: COLORS.white }}>
      <View style={{ paddingTop: 60, paddingHorizontal: 16, borderBottomWidth: 4, borderBottomColor: COLORS.black, paddingBottom: 12 }}>
        <Text style={{ color: COLORS.midGray, fontSize: 11, textTransform: "uppercase" }}>Step 2 of 9</Text>
        <Text style={{ color: COLORS.black, fontSize: 28, fontWeight: "bold", fontFamily: "Times New Roman" }}>TRADING STYLE</Text>
      </View>
      
      <View style={{ paddingHorizontal: 16, borderBottomWidth: 1, borderBottomColor: COLORS.gray, paddingBottom: 16 }}>
        <Text style={{ color: COLORS.black, fontSize: 14, fontWeight: "bold", textTransform: "uppercase", marginBottom: 12 }}>Style</Text>
        {STYLES.map((s) => (
          <TouchableOpacity
            key={s.id}
            onPress={() => setStyle(s.id)}
            style={{
              flexDirection: "row",
              justifyContent: "space-between",
              alignItems: "center",
              padding: 14,
              marginBottom: 8,
              borderWidth: 1,
              borderColor: style === s.id ? COLORS.black : COLORS.gray,
              backgroundColor: style === s.id ? COLORS.black : COLORS.white,
            }}
          >
            <Text style={{ color: style === s.id ? COLORS.white : COLORS.black, fontWeight: "bold", fontSize: 13 }}>{s.label}</Text>
            <Text style={{ color: style === s.id ? COLORS.gray : COLORS.midGray, fontSize: 11 }}>{s.desc}</Text>
          </TouchableOpacity>
        ))}
      </View>
      
      <View style={{ paddingHorizontal: 16, paddingTop: 16 }}>
        <Text style={{ color: COLORS.black, fontSize: 14, fontWeight: "bold", textTransform: "uppercase", marginBottom: 12 }}>Experience</Text>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 0 }}>
          {EXPERIENCE.map((e) => (
            <TouchableOpacity
              key={e.id}
              onPress={() => setExperience(e.id)}
              style={{
                paddingVertical: 10,
                paddingHorizontal: 14,
                borderWidth: 1,
                borderColor: experience === e.id ? COLORS.black : COLORS.gray,
                backgroundColor: experience === e.id ? COLORS.black : COLORS.white,
                marginRight: 8,
                marginBottom: 8,
              }}
            >
              <Text style={{ color: experience === e.id ? COLORS.white : COLORS.black, fontWeight: "bold", fontSize: 11 }}>{e.label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
      
      <View style={{ flex: 1 }} />
      
      <View style={{ padding: 16, borderTopWidth: 4, borderTopColor: COLORS.black }}>
        <TouchableOpacity
          onPress={handleNext}
          disabled={!style || !experience || loading}
          style={{
            backgroundColor: style && experience && !loading ? COLORS.black : COLORS.gray,
            paddingVertical: 16,
            borderWidth: 1,
            borderColor: style && experience && !loading ? COLORS.black : COLORS.midGray,
          }}
        >
          <Text style={{ color: COLORS.white, textAlign: "center", fontWeight: "bold", fontSize: 14, textTransform: "uppercase", letterSpacing: 2 }}>
            {loading ? "SAVING..." : "NEXT"}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}
