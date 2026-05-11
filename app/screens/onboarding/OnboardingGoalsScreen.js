import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, ScrollView } from "react-native";
import { useNavigation } from "@react-navigation/native";

import api from "../../services/api";

export default function OnboardingGoalsScreen() {
  const navigation = useNavigation();
  const [goals, setGoals] = useState([{ title: "", target_value: "" }]);
  const [loading, setLoading] = useState(false);

  const updateGoal = (index, field, value) => {
    setGoals((prev) =>
      prev.map((g, i) => (i === index ? { ...g, [field]: value } : g))
    );
  };

  const addGoal = () => setGoals((prev) => [...prev, { title: "", target_value: "" }]);

  const removeGoal = (index) =>
    setGoals((prev) => prev.filter((_, i) => i !== index));

  const handleNext = async () => {
    const validGoals = goals
      .filter((g) => g.title.trim())
      .map((g) => ({
        title: g.title,
        target_value: g.target_value ? parseFloat(g.target_value) : null,
      }));

    setLoading(true);
    try {
      await api.post("/onboarding/step-4", { goals: validGoals });
      navigation.navigate("OnboardingRisk");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView className="flex-1 bg-dark-900">
      <View className="px-6 pt-12 pb-6">
        <Text className="text-brand-400 text-sm font-semibold mb-2">Step 4 of 9</Text>
        <Text className="text-white text-2xl font-bold mb-2">Your Goals</Text>
        <Text className="text-dark-600 mb-6">
          What are you working towards? The AI tracks these for you.
        </Text>

        {goals.map((goal, index) => (
          <View key={index} className="bg-dark-800 rounded-xl p-4 mb-3 border border-dark-700">
            <View className="flex-row justify-between items-center mb-2">
              <Text className="text-white font-semibold">Goal {index + 1}</Text>
              {goals.length > 1 && (
                <TouchableOpacity onPress={() => removeGoal(index)}>
                  <Text className="text-red-400 text-sm">Remove</Text>
                </TouchableOpacity>
              )}
            </View>
            <TextInput
              className="bg-dark-700 text-white px-3 py-2 rounded-lg mb-2 border border-dark-600"
              placeholder="e.g. Reach $10k portfolio"
              placeholderTextColor="#64748b"
              value={goal.title}
              onChangeText={(t) => updateGoal(index, "title", t)}
            />
            <TextInput
              className="bg-dark-700 text-white px-3 py-2 rounded-lg border border-dark-600"
              placeholder="Target value (USD)"
              placeholderTextColor="#64748b"
              keyboardType="numeric"
              value={goal.target_value}
              onChangeText={(t) => updateGoal(index, "target_value", t)}
            />
          </View>
        ))}

        <TouchableOpacity onPress={addGoal} className="items-center mb-6">
          <Text className="text-brand-400 font-semibold">+ Add another goal</Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={handleNext}
          disabled={loading}
          className="bg-brand-500 py-4 rounded-xl items-center"
        >
          <Text className="text-white font-semibold text-lg">
            {loading ? "Saving..." : "Next"}
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}
