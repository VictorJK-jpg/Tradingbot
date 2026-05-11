import { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from "react-native";
import { useNavigation } from "@react-navigation/native";

import api from "../services/api";
import useAuthStore from "../store/authStore";

export default function RegisterScreen() {
  const navigation = useNavigation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    if (!email || !password) {
      Alert.alert("Error", "Please fill in all fields");
      return;
    }
    if (password !== confirmPassword) {
      Alert.alert("Error", "Passwords do not match");
      return;
    }
    setLoading(true);
    try {
      const response = await api.post("/auth/register", {
        email,
        password,
      });
      await useAuthStore.getState().setTokens(response.data);
    } catch (err) {
      Alert.alert(
        "Registration failed",
        err.response?.data?.detail || "Something went wrong"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      className="flex-1 bg-dark-900"
    >
      <View className="flex-1 justify-center px-6">
        <Text className="text-white text-3xl font-bold mb-2">
          Create account
        </Text>
        <Text className="text-dark-600 mb-8">
          Start your AI-powered trading journey
        </Text>

        <TextInput
          className="bg-dark-800 text-white px-4 py-3 rounded-xl mb-4 border border-dark-700"
          placeholder="Email"
          placeholderTextColor="#64748b"
          keyboardType="email-address"
          autoCapitalize="none"
          value={email}
          onChangeText={setEmail}
        />

        <TextInput
          className="bg-dark-800 text-white px-4 py-3 rounded-xl mb-4 border border-dark-700"
          placeholder="Password"
          placeholderTextColor="#64748b"
          secureTextEntry
          value={password}
          onChangeText={setPassword}
        />

        <TextInput
          className="bg-dark-800 text-white px-4 py-3 rounded-xl mb-6 border border-dark-700"
          placeholder="Confirm Password"
          placeholderTextColor="#64748b"
          secureTextEntry
          value={confirmPassword}
          onChangeText={setConfirmPassword}
        />

        <TouchableOpacity
          onPress={handleRegister}
          disabled={loading}
          className="bg-brand-500 py-4 rounded-xl items-center"
        >
          <Text className="text-white font-semibold text-lg">
            {loading ? "Creating account..." : "Get Started"}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => navigation.navigate("Login")}
          className="mt-6 items-center"
        >
          <Text className="text-dark-600">
            Already have an account?{" "}
            <Text className="text-brand-400 font-semibold">Sign in</Text>
          </Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}
