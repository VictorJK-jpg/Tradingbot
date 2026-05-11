import { View, Text, TouchableOpacity } from "react-native";
import { useNavigation } from "@react-navigation/native";

export default function OnboardingWelcomeScreen() {
  const navigation = useNavigation();

  return (
    <View className="flex-1 bg-dark-900 px-6 justify-center">
      <View className="items-center mb-8">
        <View className="w-20 h-20 bg-brand-500 rounded-2xl items-center justify-center mb-6">
          <Text className="text-white text-3xl font-bold">AI</Text>
        </View>
        <Text className="text-white text-3xl font-bold text-center mb-3">
          Your AI Trading Partner
        </Text>
        <Text className="text-dark-600 text-center text-base leading-6">
          Multi-source intelligence, personalised strategies, and full control over every trade decision.
        </Text>
      </View>

      <TouchableOpacity
        onPress={() => navigation.navigate("OnboardingPersona")}
        className="bg-brand-500 py-4 rounded-xl items-center"
      >
        <Text className="text-white font-semibold text-lg">Get Started</Text>
      </TouchableOpacity>

      <Text className="text-dark-600 text-center mt-4 text-sm">
        9 quick steps to personalise your experience
      </Text>
    </View>
  );
}
