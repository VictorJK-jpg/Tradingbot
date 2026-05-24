import React from "react";
import { View, Text, TouchableOpacity } from "react-native";
import { useNavigation } from "@react-navigation/native";

const COLORS = {
  white: "#F9F9F7",
  black: "#111111",
  gray: "#E5E5E0",
  red: "#CC0000",
  midGray: "#737373",
};

export default function OnboardingWelcomeScreen() {
  const navigation = useNavigation();

  return (
    <View style={{ flex: 1, backgroundColor: COLORS.white, paddingHorizontal: 20, justifyContent: "center" }}>
      <View style={{ borderBottomWidth: 4, borderBottomColor: COLORS.black, paddingBottom: 20, marginBottom: 32 }}>
        <View style={{ width: 80, height: 80, backgroundColor: COLORS.black, alignItems: "center", justifyContent: "center", marginBottom: 20 }}>
          <Text style={{ color: COLORS.white, fontSize: 28, fontWeight: "bold" }}>AI</Text>
        </View>
        <Text style={{ color: COLORS.black, fontSize: 32, fontWeight: "bold", fontFamily: "Times New Roman", textAlign: "center" }}>
          YOUR AI TRADING PARTNER
        </Text>
      </View>
      
      <Text style={{ color: COLORS.midGray, fontSize: 14, textAlign: "center", lineHeight: 22, fontFamily: "Times New Roman" }}>
        Multi-source intelligence, personalised strategies, and full control over every trade decision.
      </Text>
      
      <TouchableOpacity
        onPress={() => navigation.navigate("OnboardingPersona")}
        style={{ backgroundColor: COLORS.black, paddingVertical: 16, marginTop: 40, borderWidth: 1, borderColor: COLORS.black }}
      >
        <Text style={{ color: COLORS.white, textAlign: "center", fontWeight: "bold", fontSize: 14, textTransform: "uppercase", letterSpacing: 2 }}>
          Get Started
        </Text>
      </TouchableOpacity>
      
      <Text style={{ color: COLORS.midGray, textAlign: "center", marginTop: 16, fontSize: 11, textTransform: "uppercase", letterSpacing: 1 }}>
        9 quick steps to personalise your experience
      </Text>
    </View>
  );
}
