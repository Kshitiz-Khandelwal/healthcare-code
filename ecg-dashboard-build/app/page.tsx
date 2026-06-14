import Hero from "@/components/sections/Hero";
import ExecutiveSummary from "@/components/sections/ExecutiveSummary";
import Pipeline from "@/components/sections/Pipeline";
import Features from "@/components/sections/Features";
import Performance from "@/components/sections/Performance";
import Prototype from "@/components/sections/Prototype";
import Predictions from "@/components/sections/Predictions";
import RiskLogic from "@/components/sections/RiskLogic";
import TechStack from "@/components/sections/TechStack";
import Dataset from "@/components/sections/Dataset";
import Conclusion from "@/components/sections/Conclusion";
import Footer from "@/components/sections/Footer";
import Navbar from "@/components/Navbar";

export const metadata = {
  title: "ECG Hybrid Classification System - Kshitiz Khandelwal",
  description:
    "Automated 12-lead ECG classification report using EfficientNet-B4, LightGBM, and PhysioNet/CinC 2020 data.",
};

export default function Page() {
  return (
    <main className="bg-slate-950 text-white">
      <Navbar />
      <Hero />
      <ExecutiveSummary />
      <Pipeline />
      <Features />
      <Performance />
      <Prototype />
      <Predictions />
      <RiskLogic />
      <TechStack />
      <Dataset />
      <Conclusion />
      <Footer />
    </main>
  );
}
