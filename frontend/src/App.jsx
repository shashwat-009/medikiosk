import { Routes, Route } from "react-router-dom";
import { KioskProvider } from "./context/KioskContext";

// Patient pages
import Welcome from "./pages/patient/Welcome";
import Identify from "./pages/patient/Identify";
import Consent from "./pages/patient/Consent";
import Interview from "./pages/patient/Interview";
import Documents from "./pages/patient/Documents";
import Processing from "./pages/patient/Processing";
import Confirmation from "./pages/patient/Confirmation";

// Doctor pages
import DoctorLogin from "./pages/doctor/Login";
import DoctorDashboard from "./pages/doctor/Dashboard";
import SessionReview from "./pages/doctor/SessionReview";

export default function App() {
  return (
    <KioskProvider>
      <Routes>
        {/* Patient / Kiosk Flow */}
        <Route path="/" element={<Welcome />} />
        <Route path="/identify" element={<Identify />} />
        <Route path="/consent" element={<Consent />} />
        <Route path="/interview" element={<Interview />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/processing" element={<Processing />} />
        <Route path="/confirmation" element={<Confirmation />} />

        {/* Doctor Flow */}
        <Route path="/doctor/login" element={<DoctorLogin />} />
        <Route path="/doctor" element={<DoctorDashboard />} />
        <Route
          path="/doctor/session/:sessionId"
          element={<SessionReview />}
        />
      </Routes>
    </KioskProvider>
  );
}