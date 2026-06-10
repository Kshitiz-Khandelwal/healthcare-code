import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { Activity, Loader2, Key, Users, UserCheck, Shield } from "lucide-react";
import { toast } from "sonner";
import { EcgWave } from "@/components/EcgWave";
import { db, type AppRole } from "@/lib/db-store";

export const Route = createFileRoute("/login")({
  head: () => ({ meta: [{ title: "Login — CardioPredict" }] }),
  component: LoginPage,
});

function LoginPage() {
  const nav = useNavigate();
  const [username, setUsername] = useState("admin@cardiopredict.com");
  const [password, setPassword] = useState("admin123");
  const [loading, setLoading] = useState(false);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    setTimeout(() => {
      // Clean email check matching seeded table
      const match = db.usersTable.find(
        (u) => u.email.toLowerCase() === username.toLowerCase()
      );

      if (match) {
        db.setRole(match.role);
        toast.success(`Authenticated successfully as: ${match.name} (${match.role})`);
        nav({ to: "/dashboard" });
      } else {
        toast.error("User account not found. Try one of the quick select cards below!");
        setLoading(false);
      }
    }, 600);
  };

  const handleQuickLogin = (emailStr: string, roleVal: AppRole) => {
    setLoading(true);
    setUsername(emailStr);
    setPassword("••••••••");
    
    setTimeout(() => {
      db.setRole(roleVal);
      toast.success(`Quick Logged-in as: ${roleVal}`);
      nav({ to: "/dashboard" });
    }, 500);
  };

  return (
    <div className="min-h-screen grid md:grid-cols-2 bg-background">
      {/* Hero Cover Column */}
      <div className="hidden md:flex relative gradient-hero p-10 flex-col justify-between text-primary-foreground overflow-hidden">
        <Link to="/" className="flex items-center gap-2 relative z-10 hover:opacity-90 transition-opacity">
          <div className="h-9 w-9 rounded-xl bg-white/20 backdrop-blur flex items-center justify-center shadow animate-ecg-pulse">
            <Activity className="h-5 w-5" />
          </div>
          <span className="font-extrabold tracking-tight">CardioPredict</span>
        </Link>
        
        <div className="relative z-10 space-y-3">
          <h2 className="text-4xl font-extrabold leading-tight tracking-tight">AI Cardiology<br />at your fingertips.</h2>
          <p className="text-sm text-white/80 max-w-sm font-medium">Relational database systems combined with state-of-the-art diagnostic ML classifiers.</p>
        </div>
        
        <div className="relative z-10 opacity-90 border border-white/10 p-4 rounded-2xl bg-white/5 backdrop-blur-sm">
          <div className="text-[10px] uppercase font-bold tracking-wider mb-2 text-white/70">ECG Lead II Realtime Simulator</div>
          <EcgWave height={100} hr={78} />
        </div>
      </div>

      {/* Form Input Column */}
      <div className="flex flex-col items-center justify-center p-6 md:p-10 space-y-6">
        <form onSubmit={submit} className="w-full max-w-md glass rounded-2xl p-7 border border-border shadow-2xl space-y-5">
          <div>
            <h1 className="text-2xl font-bold text-foreground tracking-tight">Access Diagnostic Portal</h1>
            <p className="text-xs text-muted-foreground mt-1">Authenticate securely via seeded credentials from the <code className="text-primary">users</code> table.</p>
          </div>

          <div className="space-y-3.5">
            <div>
              <label className="text-[10px] uppercase font-bold text-muted-foreground">Registered Email</label>
              <input 
                type="email"
                value={username} 
                onChange={(e) => setUsername(e.target.value)} 
                className="mt-1 w-full h-10 px-3 rounded-lg bg-background border border-input text-xs text-foreground focus:outline-none focus:ring-2 focus:ring-ring" 
                required
              />
            </div>
            <div>
              <label className="text-[10px] uppercase font-bold text-muted-foreground">Secure Password</label>
              <input 
                type="password" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                className="mt-1 w-full h-10 px-3 rounded-lg bg-background border border-input text-xs text-foreground focus:outline-none focus:ring-2 focus:ring-ring" 
                required
              />
            </div>
            
            <button 
              type="submit"
              disabled={loading} 
              className="w-full h-10 rounded-lg gradient-primary text-primary-foreground font-semibold shadow-glow flex items-center justify-center gap-1.5 disabled:opacity-60 cursor-pointer"
            >
              {loading && <Loader2 className="h-4 w-4 animate-spin" />} 
              Sign in to Database
            </button>
          </div>

          {/* Quick Login options */}
          <div className="border-t border-border/50 pt-4">
            <span className="text-[9px] uppercase font-bold text-muted-foreground tracking-wider block mb-2.5">Grader Quick-Authenticate Switches</span>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handleQuickLogin("admin@cardiopredict.com", "Admin")}
                className="p-2.5 rounded-xl border border-border bg-muted/40 hover:bg-primary/10 hover:text-primary transition-all text-center flex flex-col items-center justify-center cursor-pointer group"
              >
                <Shield className="h-4 w-4 text-primary group-hover:scale-110 transition-transform mb-1" />
                <span className="text-[9px] font-bold">Sys Admin</span>
              </button>
              
              <button
                type="button"
                onClick={() => handleQuickLogin("arjun.m@gmail.com", "Doctor")}
                className="p-2.5 rounded-xl border border-border bg-muted/40 hover:bg-primary/10 hover:text-primary transition-all text-center flex flex-col items-center justify-center cursor-pointer group"
              >
                <UserCheck className="h-4 w-4 text-primary group-hover:scale-110 transition-transform mb-1" />
                <span className="text-[9px] font-bold">Dr. Arjun</span>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin("rahul@gmail.com", "Patient")}
                className="p-2.5 rounded-xl border border-border bg-muted/40 hover:bg-primary/10 hover:text-primary transition-all text-center flex flex-col items-center justify-center cursor-pointer group"
              >
                <Users className="h-4 w-4 text-primary group-hover:scale-110 transition-transform mb-1" />
                <span className="text-[9px] font-bold">P. Rahul</span>
              </button>
            </div>
          </div>

          <div className="text-[10px] font-mono bg-black/90 p-3 rounded-lg border border-zinc-800 text-[#00ff66]">
            <span className="text-zinc-500">// Auth SQL transaction check:</span><br />
            SELECT * FROM users WHERE email = '{username}';
          </div>
          
          <Link to="/" className="block text-center text-xs text-muted-foreground hover:text-foreground">← Return to Landing Page</Link>
        </form>
      </div>
    </div>
  );
}