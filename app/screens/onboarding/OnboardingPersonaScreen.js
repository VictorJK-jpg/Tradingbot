import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity } from "react-native";
import { useNavigation } from "@react-navigation/native";

import api from "../../services/api";

export default function OnboardingPersonaScreen() {
  const navigation = useNavigation();
  const [name, setName] = useState("");
  const [personality, setPersonality] = useState("");
  const [loading, setLoading] = useState(false);

  const handleNext = async () => {
    if (!name.trim()) return;
    setLoading(true);
    try {
      await api.post("/onboarding/step-1", {
        persona_name: name,
        personality: personality || null,
      });
      navigation.navigate("OnboardingTraderStyle");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View className="flex-1 bg-dark-900 px-6 pt-12">
      <Text className="text-brand-400 text-sm font-semibold mb-2">Step 1 of 9</Text>
      <Text className="text-white text-2xl font-bold mb-2">Name Your AI</Text>
      <Text className="text-dark-600 mb-8">
        What would you like to call your trading assistant?
      </Text>

      <TextInput
        className="bg-dark-800 text-white px-4 py-3 rounded-xl mb-4 border border-dark-700"
        placeholder="e.g. Alpha, Sage, Titan..."
        placeholderTextColor="#64748b"
        value={name}
        onChangeText={setName}
      />

      <Text className="text-white font-semibold mb-3">Personality (optional)</Text>
      <TextInput
        className="bg-dark-800 text-white px-4 py-3 rounded-xl mb-6 border border-dark-700 h-24"
        placeholder="e.g. calm and analytical, aggressive and bold..."
        placeholderTextColor="#64748b"
        multiline
        textAlignVertical="top"
        value={personality}
        onChangeText={setPersonality}
      />

      <TouchableOpacity
        onPress={handleNext}
        disabled={!name.trim() || loading}
        className={`py-4 rounded-xl items-center ${
          name.trim() && !loading ? "bg-brand-500" : "bg-dark-700"
        }`}
      >
        <Text className="text-white font-semibold text-lg">
          {loading ? "Saving..." : "Next"}
        </Text>
      </TouchableOpacity>
    </View>
  );
}
