import { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
} from "react-native";

import api from "../services/api";

const EXCHANGES = [
  { id: "binance", name: "Binance", testnet: true },
  { id: "bybit", name: "Bybit", testnet: true },
  { id: "coinbase", name: "Coinbase", testnet: false },
  { id: "kraken", name: "Kraken", testnet: false },
];

export default function ExchangeScreen() {
  const [selectedExchange, setSelectedExchange] = useState("binance");
  const [apiKey, setApiKey] = useState("");
  const [apiSecret, setApiSecret] = useState("");
  const [useTestnet, setUseTestnet] = useState(true);
  const [loading, setLoading] = useState(false);

  const handleConnect = async () => {
    if (!apiKey || !apiSecret) {
      Alert.alert("Error", "Please enter both API key and secret");
      return;
    }
    setLoading(true);
    try {
      await api.post("/exchange/connections", {
        exchange: selectedExchange,
        api_key: apiKey,
        api_secret: apiSecret,
        is_testnet: useTestnet,
      });
      Alert.alert("Success", "Exchange connected successfully");
      setApiKey("");
      setApiSecret("");
    } catch (err) {
      Alert.alert(
        "Connection failed",
        err.response?.data?.detail || "Could not connect to exchange"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView className="flex-1 bg-dark-900">
      <View className="px-5 pt-12 pb-6">
        <Text className="text-white text-2xl font-bold mb-1">
          Connect Exchange
        </Text>
        <Text className="text-dark-600 mb-6">
          Link your exchange API (trade-only permissions)
        </Text>

        {/* Exchange Selector */}
        <Text className="text-white font-semibold mb-3">Select Exchange</Text>
        <View className="flex-row flex-wrap gap-2 mb-6">
          {EXCHANGES.map((ex) => (
            <TouchableOpacity
              key={ex.id}
              onPress={() => {
                setSelectedExchange(ex.id);
                setUseTestnet(ex.testnet);
              }}
              className={`px-4 py-2 rounded-xl border ${
                selectedExchange === ex.id
                  ? "bg-brand-500 border-brand-500"
                  : "bg-dark-800 border-dark-700"
              }`}
            >
              <Text
                className={`font-semibold ${
                  selectedExchange === ex.id ? "text-white" : "text-dark-600"
                }`}
              >
                {ex.name}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Testnet Toggle */}
        <View className="flex-row items-center mb-6">
          <TouchableOpacity
            onPress={() => setUseTestnet(!useTestnet)}
            className={`w-6 h-6 rounded border mr-3 items-center justify-center ${
              useTestnet
                ? "bg-brand-500 border-brand-500"
                : "bg-dark-800 border-dark-600"
            }`}
          >
            {useTestnet && <Text className="text-white text-xs">✓</Text>}
          </TouchableOpacity>
          <Text className="text-white">Use testnet (sandbox)</Text>
        </View>

        {/* API Key Inputs */}
        <Text className="text-white font-semibold mb-3">API Credentials</Text>
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
          onPress={handleConnect}
          disabled={loading}
          className="bg-brand-500 py-4 rounded-xl items-center"
        >
          <Text className="text-white font-semibold text-lg">
            {loading ? "Connecting..." : "Connect Exchange"}
          </Text>
        </TouchableOpacity>

        <View className="mt-6 p-4 bg-dark-800 rounded-xl border border-dark-700">
          <Text className="text-brand-400 font-semibold mb-2">
            Security Notice
          </Text>
          <Text className="text-dark-600 text-sm">
            • Keys are encrypted at rest using Fernet{"\n"}
            • Use trade-only API permissions{"\n"}
            • Never enable withdrawal permissions{"\n"}
            • We recommend starting with testnet
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}
