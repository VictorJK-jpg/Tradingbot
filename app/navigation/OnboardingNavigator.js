import { createNativeStackNavigator } from "@react-navigation/native-stack";

import OnboardingWelcomeScreen from "../screens/onboarding/OnboardingWelcomeScreen";
import OnboardingPersonaScreen from "../screens/onboarding/OnboardingPersonaScreen";
import OnboardingTraderStyleScreen from "../screens/onboarding/OnboardingTraderStyleScreen";
import OnboardingPsychScreen from "../screens/onboarding/OnboardingPsychScreen";
import OnboardingGoalsScreen from "../screens/onboarding/OnboardingGoalsScreen";
import OnboardingRiskScreen from "../screens/onboarding/OnboardingRiskScreen";
import OnboardingAssetsScreen from "../screens/onboarding/OnboardingAssetsScreen";
import OnboardingExchangeScreen from "../screens/onboarding/OnboardingExchangeScreen";
import OnboardingStrategyScreen from "../screens/onboarding/OnboardingStrategyScreen";
import OnboardingCompleteScreen from "../screens/onboarding/OnboardingCompleteScreen";

const Stack = createNativeStackNavigator();

export default function OnboardingNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="OnboardingWelcome" component={OnboardingWelcomeScreen} />
      <Stack.Screen name="OnboardingPersona" component={OnboardingPersonaScreen} />
      <Stack.Screen name="OnboardingTraderStyle" component={OnboardingTraderStyleScreen} />
      <Stack.Screen name="OnboardingPsych" component={OnboardingPsychScreen} />
      <Stack.Screen name="OnboardingGoals" component={OnboardingGoalsScreen} />
      <Stack.Screen name="OnboardingRisk" component={OnboardingRiskScreen} />
      <Stack.Screen name="OnboardingAssets" component={OnboardingAssetsScreen} />
      <Stack.Screen name="OnboardingExchange" component={OnboardingExchangeScreen} />
      <Stack.Screen name="OnboardingStrategy" component={OnboardingStrategyScreen} />
      <Stack.Screen name="OnboardingComplete" component={OnboardingCompleteScreen} />
    </Stack.Navigator>
  );
}
