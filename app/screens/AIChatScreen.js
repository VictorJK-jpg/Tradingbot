import { useState, useRef, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from "react-native";

import api from "../services/api";

const SKILL_BADGES = {
  strategies: { bg: "bg-blue-900", text: "text-blue-400", label: "STRAT" },
  risk_management: { bg: "bg-red-900", text: "text-red-400", label: "RISK" },
  market_reading: { bg: "bg-purple-900", text: "text-purple-400", label: "MARKET" },
  fundamental: { bg: "bg-green-900", text: "text-green-400", label: "FUND" },
  weekly_outlook: { bg: "bg-yellow-900", text: "text-yellow-400", label: "MACRO" },
};

export default function AIChatScreen() {
  const [messages, setMessages] = useState([
    {
      id: "1",
      role: "assistant",
      content: "👋 Welcome to your AI trading assistant! Ask me about market analysis, trade ideas, or risk management strategies.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [lastSkills, setLastSkills] = useState([]);
  const scrollRef = useRef();

  const scrollToBottom = () => {
    scrollRef.current?.scrollToEnd({ animated: true });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await api.post("/ai/ask", {
        message: userMessage.content,
        coin_ids: ["bitcoin", "ethereum"],
        include_market: true,
      });

      // Extract skills from response
      const skillsLoaded = response.data.skills_loaded || [];
      setLastSkills(skillsLoaded);

      const aiMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.data.response,
        skills: skillsLoaded,
        budget_remaining: response.data.budget_remaining,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Failed to get AI response";
      Alert.alert("Error", errorMsg);
      
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `⚠️ ${errorMsg}. Please try again.`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const renderSkillBadge = (skill) => {
    const [category] = skill.split("/");
    const badge = SKILL_BADGES[category] || SKILL_BADGES.strategies;
    return (
      <View key={skill} className={`${badge.bg} px-2 py-1 rounded mr-2 mb-1`}>
        <Text className={`${badge.text} text-xs font-semibold`}>
          {badge.label}
        </Text>
      </View>
    );
  };

  const renderMessage = (msg) => {
    const isUser = msg.role === "user";
    return (
      <View
        key={msg.id}
        className={`px-5 py-3 ${isUser ? "bg-dark-800" : "bg-transparent"}`}
      >
        <View
          className={`max-w-[85%] rounded-2xl p-4 ${
            isUser
              ? "bg-brand-600 self-end rounded-br-none"
              : "bg-dark-800 self-start rounded-bl-none border border-dark-700"
          }`}
        >
          <Text className={`${isUser ? "text-white" : "text-dark-300"} leading-relaxed`}>
            {msg.content}
          </Text>
          
          {/* Skills badges for AI messages */}
          {msg.skills && msg.skills.length > 0 && (
            <View className="flex-row flex-wrap mt-3">
              {msg.skills.map((skill) => renderSkillBadge(skill))}
            </View>
          )}

          {/* Budget info */}
          {msg.budget_remaining !== undefined && (
            <View className="mt-2 pt-2 border-t border-dark-700">
              <Text className="text-dark-500 text-xs">
                Budget remaining: {msg.budget_remaining}/50
              </Text>
            </View>
          )}
        </View>
      </View>
    );
  };

  return (
    <KeyboardAvoidingView
      className="flex-1 bg-dark-900"
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      keyboardVerticalOffset={90}
    >
      {/* Header */}
      <View className="pt-12 pb-4 px-5 border-b border-dark-800">
        <View className="flex-row justify-between items-center">
          <View>
            <Text className="text-white text-xl font-bold">AI Trading Assistant</Text>
            <Text className="text-dark-600 text-sm">Powered by advanced market intelligence</Text>
          </View>
          <View className="flex-row gap-2">
            {lastSkills.slice(0, 3).map((skill) => renderSkillBadge(skill))}
          </View>
        </View>
      </View>

      {/* Messages */}
      <ScrollView ref={scrollRef} className="flex-1 py-4">
        {messages.map(renderMessage)}
        
        {/* Loading indicator */}
        {loading && (
          <View className="px-5 py-3">
            <View className="bg-dark-800 rounded-2xl p-4 max-w-[70%] rounded-bl-none border border-dark-700">
              <View className="flex-row items-center gap-2">
                <View className="w-2 h-2 bg-brand-400 rounded-full animate-pulse" />
                <Text className="text-dark-400">Analyzing...</Text>
              </View>
            </View>
          </View>
        )}
      </ScrollView>

      {/* Quick suggestions */}
      {!loading && messages.length === 1 && (
        <View className="px-5 pb-2">
          <Text className="text-dark-600 text-xs mb-2">Try asking:</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} className="flex-row gap-2">
            {["Should I long BTC?", "Analyze ETH trend", "Risk management tips"].map(
              (suggestion) => (
                <TouchableOpacity
                  key={suggestion}
                  onPress={() => setInput(suggestion)}
                  className="bg-dark-800 px-4 py-2 rounded-full border border-dark-700"
                >
                  <Text className="text-dark-400 text-sm">{suggestion}</Text>
                </TouchableOpacity>
              )
            )}
          </ScrollView>
        </View>
      )}

      {/* Input */}
      <View className="px-5 pb-6 pt-2 border-t border-dark-800">
        <View className="flex-row gap-3">
          <TextInput
            className="flex-1 bg-dark-800 text-white px-4 py-3 rounded-xl border border-dark-700"
            placeholder="Ask about trades, markets, or strategies..."
            placeholderTextColor="#64748b"
            value={input}
            onChangeText={setInput}
            multiline
            maxLength={4000}
          />
          <TouchableOpacity
            onPress={sendMessage}
            disabled={loading || !input.trim()}
            className={`px-5 py-3 rounded-xl ${
              loading || !input.trim() ? "bg-dark-700" : "bg-brand-500"
            }`}
          >
            <Text className="text-white text-lg">➤</Text>
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}