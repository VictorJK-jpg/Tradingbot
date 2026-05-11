import { useEffect } from "react";
import { View, Text, TouchableOpacity } from "react-native";
import { useNavigation, CommonActions } from "@react-navigation/native";

import api from "../../services/api";
import useAuthStore from "../../store/authStore";

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
    <View className="flex-1 bg-dark-900 px-6 justify-center items-center">
      <View className="w-20 h-20 bg-brand-500 rounded-2xl items-center justify-center mb-6">
        <Text className="text-white text-3xl font-bold">✓</Text>
      </View>
      <Text className="text-white text-3xl font-bold mb-3 text-center">
        You're All Set!
      </Text>
      <Text className="text-dark-600 text-center text-base leading-6 mb-8">
        Your AI trading partner is configured and ready. All decisions will be personalised to your profile.
      </Text>

      <TouchableOpacity
        onPress={goToMain}
        className="bg-brand-500 py-4 rounded-xl items-center w-full"
      >
        <Text className="text-white font-semibold text-lg">Go to Dashboard</Text>
      </TouchableOpacity>
    </View>
  );
}
