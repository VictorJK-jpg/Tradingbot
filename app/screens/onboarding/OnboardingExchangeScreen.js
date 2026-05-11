import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, Alert } from "react-native";
import { useNavigation } from "@react-navigation/native";

import api from "../../services/api";

const EXCHANGES = [
  { id: "binance", name: "Binance", testnet: true },
  { id: "bybit", name: "Bybit", testnet: true },
];

export default function OnboardingExchangeScreen() {
  const navigation = useNavigation();
  const [exchange, setExchange] = useState("binance");
  const [apiKey, setApiKey] = useState("");
  const [apiSecret, setApiSecret] = useState("");
  const [useTestnet, setUseTestnet] = useState(true);
  const [loading, setLoading] = useState(false);

  const handleNext = async () => {
    if (!apiKey || !apiSecret) {
      Alert.alert("Required", "Please enter your API key and secret");
      return;
    }
    setLoading(true);
    try {
      await api.post("/onboarding/step-7", {
        exchange,
        api_key: apiKey,
        api_secret: apiSecret,
        is_testnet: useTestnet,
      });
      navigation.navigate("OnboardingStrategy");
    } catch (err) {
      Alert.alert("Error", err.response?.data?.detail || "Could not save exchange connection");
    } finally {
      setLoading(false);
    }
  };

  const skip = async () => {
    setLoading(true);
    try {
      await api.post("/onboarding/step-7", {
        exchange: null,
        api_key: null,
        api_secret: null,
        is_testnet: true,
      });
    } catch {
      // ignore
    }
    navigation.navigate("OnboardingStrategy");
    setLoading(false);
  };

  return (
    <View className="flex-1 bg-dark-900 px-6 pt-12">
      <Text className="text-brand-400 text-sm font-semibold mb-2">Step 7 of 9</Text>
      <Text className="text-white text-2xl font-bold mb-2">Connect Exchange</Text>
      <Text className="text-dark-600 mb-6">
        Trade-only API keys. No withdrawal permissions.
      </Text>

      <View className="flex-row gap-2 mb-4">
        {EXCHANGES.map((ex) => (
          <TouchableOpacity
            key={ex.id}
            onPress={() => {
              setExchange(ex.id);
              setUseTestnet(ex.testnet);
            }}
            className={`flex-1 py-3 rounded-xl items-center border ${
              exchange === ex.id ? "bg-brand-500 border-brand-500" : "bg-dark-800 border-dark-700"
            }`}
          >
            <Text className={`font-semibold ${exchange === ex.id ? "text-white" : "text-dark-600"}`}>
              {ex.name}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <View className="flex-row items-center mb-4">
        <TouchableOpacity
          onPress={() => setUseTestnet(!useTestnet)}
          className={`w-6 h-6 rounded border mr-3 items-center justify-center ${
            useTestnet ? "bg-brand-500 border-brand-500" : "bg-dark-800 border-dark-600"
          }`}
        >
          {useTestnet && <Text className="text-white text-xs">✓</Text>}
        </TouchableOpacity>
        <Text className="text-white">Use testnet (recommended)</Text>
      </View>

      <TextInput
        className="bg-dark-800 text-white px-4 py-3 rounded-xl mb-4 border border-dark-700"
        placeholder="API Key"
        placeholderTextColor="#64748b"
        value={apiKey}
        onChangeText={setApiKey}
        autoCapitalize="none"
      />
      <TextInput
        className="bg-dark-800 text-white px-4 py-3 rounded-xl mb-6 border border-dark-700"
        placeholder="API Secret"
        placeholderTextColor="#64748b"
        value={apiSecret}
        onChangeText={setApiSecret}
        autoCapitalize="none"
        secureTextEntry
      />

      <TouchableOpacity
        onPress={handleNext}
        disabled={loading}
        className="bg-brand-500 py-4 rounded-xl items-center mb-3"
      >
        <Text className="text-white font-semibold text-lg">
          {loading ? "Connecting..." : "Connect & Continue"}
        </Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={skip} className="items-center">
        <Text className="text-dark-600">Skip for now</Text>
      </TouchableOpacity>
    </View>
  );
}
