import { View, Text, TouchableOpacity, Alert } from "react-native";

import useAuthStore from "../store/authStore";

export default function SettingsScreen() {
  const clearTokens = useAuthStore((s) => s.clearTokens);

  const handleLogout = () => {
    Alert.alert("Sign Out", "Are you sure you want to sign out?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Sign Out",
        style: "destructive",
        onPress: () => clearTokens(),
      },
    ]);
  };

  return (
    <View className="flex-1 bg-dark-900 px-5 pt-12">
      <Text className="text-white text-2xl font-bold mb-6">Settings</Text>

      <View className="bg-dark-800 rounded-2xl border border-dark-700 overflow-hidden mb-4">
        <TouchableOpacity className="px-5 py-4 border-b border-dark-700">
          <Text className="text-white font-semibold">Edit Profile</Text>
        </TouchableOpacity>
        <TouchableOpacity className="px-5 py-4 border-b border-dark-700">
          <Text className="text-white font-semibold">Risk Budget</Text>
        </TouchableOpacity>
        <TouchableOpacity className="px-5 py-4 border-b border-dark-700">
          <Text className="text-white font-semibold">Notifications</Text>
        </TouchableOpacity>
        <TouchableOpacity className="px-5 py-4">
          <Text className="text-white font-semibold">AI Preferences</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity
        onPress={handleLogout}
        className="bg-red-900/30 py-4 rounded-xl items-center border border-red-900/50"
      >
        <Text className="text-red-400 font-semibold text-lg">Sign Out</Text>
      </TouchableOpacity>
    </View>
  );
}
