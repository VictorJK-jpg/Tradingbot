import React, { useEffect } from "react";
import { View, Text, TouchableOpacity } from "react-native";
import { useNavigation, CommonActions } from "@react-navigation/native";

import api from "../../services/api";
import useAuthStore from "../../store/authStore";

const COLORS = {
  white: "#F9F9F7",
  black: "#111111",
  gray: "#E5E5E0",
  red: "#CC0000",
  midGray: "#737373",
};

export default function OnboardingCompleteScreen() {
  const navigation = useNavigation();
  const setUser = useAuthStore((s) => s.setUser);

  useEffect(() => {
    const complete = async () => {
      try {
        await api.post("/onboarding/complete");
        const me = await api.get("/users/me");
        setUser(me.data);
      } catch (err) {
        console.error("Failed to complete onboarding", err);
      }
    };
    complete();
  }, [setUser]);

  const goToMain = () => {
    navigation.dispatch(
      CommonActions.reset({
        index: 0,
        routes: [{ name: "Main" }],
      })
    );
  };

  return (
    <View style={{ flex: 1, backgroundColor: COLORS.white, paddingHorizontal: 20, justifyContent: "center", alignItems: "center" }}>
      <View style={{ width: 80, height: 80, backgroundColor: COLORS.black, alignItems: "center", justifyContent: "center", marginBottom: 24 }}>
        <Text style={{ color: COLORS.white, fontSize: 36, fontWeight: "bold" }}>✓</Text>
      </View>
      
      <Text style={{ color: COLORS.black, fontSize: 32, fontWeight: "bold", fontFamily: "Times New Roman", textAlign: "center", marginBottom: 16 }}>
        YOU'RE ALL SET!
      </Text>
      
      <Text style={{ color: COLORS.midGray, fontSize: 14, textAlign: "center", lineHeight: 22, fontFamily: "Times New Roman", paddingHorizontal: 20 }}>
        Your AI trading partner is configured and ready. All decisions will be personalised to your profile.
      </Text>

      <TouchableOpacity
        onPress={goToMain}
        style={{ backgroundColor: COLORS.black, paddingVertical: 16, paddingHorizontal: 40, marginTop: 40, borderWidth: 1, borderColor: COLORS.black }}
      >
        <Text style={{ color: COLORS.white, textAlign: "center", fontWeight: "bold", fontSize: 14, textTransform: "uppercase", letterSpacing: 2 }}>
          GO TO DASHBOARD
        </Text>
      </TouchableOpacity>
    </View>
  );
}
