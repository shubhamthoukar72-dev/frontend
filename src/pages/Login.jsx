import { useRef, useState } from "react";
import {
  ArrowRight,
  BriefcaseBusiness,
  CheckCircle2,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  Sparkles,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import Toast from "../components/Toast";
import { saveAuthSession, signIn } from "../services/auth";

function Login() {
  const navigate = useNavigate();
  const submitLock = useRef(false);

  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState(
    () => localStorage.getItem("jobai_remembered_email") || ""
  );
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(
    () => localStorage.getItem("jobai_remember_me") === "true"
  );
  const [toast, setToast] = useState(null);
  const [loading, setLoading] = useState(false);
  const [formErrors, setFormErrors] = useState({
    email: "",
    password: "",
  });

  const validateForm = () => {
    const cleanEmail = email.trim().toLowerCase();
    const nextErrors = {
      email: "",
      password: "",
    };

    if (!cleanEmail) {
      nextErrors.email = "Email is required.";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cleanEmail)) {
      nextErrors.email = "Please enter a valid email address.";
    }

    if (!password) {
      nextErrors.password = "Password is required.";
    }

    setFormErrors(nextErrors);

    return !nextErrors.email && !nextErrors.password;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (submitLock.current || loading) {
      return;
    }

    if (!validateForm()) {
      return;
    }

    try {
      submitLock.current = true;
      setLoading(true);
      const cleanEmail = email.trim().toLowerCase();
      const data = await signIn(cleanEmail, password);
      saveAuthSession(data, cleanEmail, rememberMe);

      setEmail("");
      setPassword("");
      setShowPassword(false);
      setFormErrors({ email: "", password: "" });

      navigate(
        data.user.role === "admin" ? "/admin/dashboard" : "/dashboard",
        { replace: true }
      );
    } catch (error) {
      setToast({
        type: "error",
        message:
          error.message ||
          "Unable to login. Please try again.",
      });
    } finally {
      submitLock.current = false;
      setLoading(false);
    }
  };

  return (
    <>
      <main className="auth-premium-page">

        <div className="auth-page-grid" aria-hidden="true"></div>

        <div
          className="auth-page-glow auth-glow-one"
          aria-hidden="true"
        ></div>

        <div
          className="auth-page-glow auth-glow-two"
          aria-hidden="true"
        ></div>

        <section className="auth-premium-container">

          {/* LEFT */}

          <div className="auth-premium-intro">

            <Link
              to="/"
              className="auth-brand"
            >
              <div className="auth-brand-icon">
                <BriefcaseBusiness size={21} />
              </div>

              <div className="auth-brand-text">
                <span>Job</span>AI
              </div>
            </Link>

            <div className="auth-intro-content">

              <div className="auth-ai-badge">
                <Sparkles size={15} />
                AI-Powered Career Platform
              </div>

              <h1>
                Welcome back.
                <br />

                <span>
                  Your next opportunity
                </span>

                <br />

                is waiting.
              </h1>

              <p>
                Sign in to continue discovering
                jobs, managing applications and
                getting smarter AI-powered career
                matches.
              </p>

              <div className="auth-feature-list">

                <div className="auth-feature-item">
                  <div>
                    <CheckCircle2 size={17} />
                  </div>

                  <span>
                    Personalized job
                    recommendations
                  </span>
                </div>

                <div className="auth-feature-item">
                  <div>
                    <CheckCircle2 size={17} />
                  </div>

                  <span>
                    AI-powered career matching
                  </span>
                </div>

                <div className="auth-feature-item">
                  <div>
                    <CheckCircle2 size={17} />
                  </div>

                  <span>
                    Simple application
                    management
                  </span>
                </div>

              </div>
            </div>

            <div className="auth-intro-footer">
              <span>© 2026 JobAI</span>

              <span>
                Smart careers. Better
                opportunities.
              </span>
            </div>

          </div>

          {/* RIGHT */}

          <div className="auth-form-wrapper">

            <div className="auth-form-card">

              <div className="auth-form-header">

                <span className="auth-form-label">
                  WELCOME BACK
                </span>

                <h2>
                  Welcome Back
                </h2>

                <p>
                  Sign in to continue to your account
                </p>

              </div>

              <form
                onSubmit={handleSubmit}
                noValidate
                aria-busy={loading}
              >

                {/* EMAIL */}

                <div className="auth-form-group">

                  <label htmlFor="login-email">
                    Email Address
                  </label>

                  <div
                    className={`auth-input-wrapper ${
                      formErrors.email ? "auth-input-error" : ""
                    }`}
                  >

                    <Mail size={18} />

                    <input
                      id="login-email"
                      name="email"
                      type="email"
                      value={email}
                      onChange={(event) => {
                        setEmail(event.target.value);
                        if (formErrors.email) {
                          setFormErrors((previous) => ({
                            ...previous,
                            email: "",
                          }));
                        }
                      }}
                      placeholder="you@example.com"
                      autoComplete="email"
                      disabled={loading}
                      required
                      aria-invalid={Boolean(formErrors.email)}
                      aria-describedby={
                        formErrors.email ? "login-email-error" : undefined
                      }
                    />

                  </div>

                  {formErrors.email && (
                    <p
                      id="login-email-error"
                      className="auth-field-error"
                      aria-live="polite"
                    >
                      {formErrors.email}
                    </p>
                  )}

                </div>

                {/* PASSWORD */}

                <div className="auth-form-group">

                  <div className="auth-label-row">

                    <label htmlFor="login-password">
                      Password
                    </label>

                    <Link
                      className="auth-forgot-button"
                      to="/forgot-password"
                    >
                      Forgot Password?
                    </Link>

                  </div>

                  <div
                    className={`auth-input-wrapper ${
                      formErrors.password ? "auth-input-error" : ""
                    }`}
                  >

                    <LockKeyhole size={18} />

                    <input
                      id="login-password"
                      name="password"
                      type={
                        showPassword
                          ? "text"
                          : "password"
                      }
                      value={password}
                      onChange={(event) => {
                        setPassword(event.target.value);
                        if (formErrors.password) {
                          setFormErrors((previous) => ({
                            ...previous,
                            password: "",
                          }));
                        }
                      }}
                      placeholder="Enter your password"
                      autoComplete="current-password"
                      disabled={loading}
                      required
                      aria-invalid={Boolean(formErrors.password)}
                      aria-describedby={
                        formErrors.password ? "login-password-error" : undefined
                      }
                    />

                    <button
                      type="button"
                      className="auth-password-toggle"
                      disabled={loading}
                      onClick={() =>
                        setShowPassword(
                          (previous) => !previous
                        )
                      }
                      aria-label={
                        showPassword
                          ? "Hide password"
                          : "Show password"
                      }
                      aria-pressed={showPassword}
                    >
                      {showPassword ? (
                        <EyeOff size={18} />
                      ) : (
                        <Eye size={18} />
                      )}
                    </button>

                  </div>

                  {formErrors.password && (
                    <p
                      id="login-password-error"
                      className="auth-field-error"
                      aria-live="polite"
                    >
                      {formErrors.password}
                    </p>
                  )}

                </div>

                <div className="auth-remember-row">
                  <label className="auth-checkbox-label" htmlFor="remember-me">
                    <input
                      id="remember-me"
                      name="rememberMe"
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(event) =>
                        setRememberMe(event.target.checked)
                      }
                      disabled={loading}
                    />
                    <span>Remember me</span>
                  </label>
                </div>

                {/* SUBMIT */}

                <button
                  type="submit"
                  className="auth-submit-button"
                  disabled={loading}
                  aria-label={loading ? "Signing in" : undefined}
                >
                  {loading ? "Signing In..." : "Sign In"}

                  {!loading && (
                    <ArrowRight size={17} />
                  )}
                </button>

              </form>

              <div className="auth-divider">
                <span>OR</span>
              </div>

              <div className="auth-register-prompt">

                <span>
                  Don't have an account?
                </span>

                <Link to="/register">
                  Sign Up
                  <ArrowRight size={15} />
                </Link>

              </div>

            </div>

          </div>

        </section>

      </main>

      {toast && (
        <Toast
          type={toast.type}
          message={toast.message}
          onClose={() => setToast(null)}
        />
      )}
    </>
  );
}

export default Login;