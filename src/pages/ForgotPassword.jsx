import { ArrowLeft, BriefcaseBusiness, Mail } from "lucide-react";
import { Link } from "react-router-dom";

function ForgotPassword() {
  return (
    <main className="auth-premium-page">
      <div className="auth-page-grid" aria-hidden="true" />
      <div className="auth-page-glow auth-glow-one" aria-hidden="true" />
      <div className="auth-page-glow auth-glow-two" aria-hidden="true" />

      <section
        className="auth-premium-container auth-reset-container"
        aria-labelledby="reset-heading"
      >
        <Link to="/" className="auth-brand">
          <div className="auth-brand-icon">
            <BriefcaseBusiness size={21} aria-hidden="true" />
          </div>
          <div className="auth-brand-text">
            <span>Job</span>AI
          </div>
        </Link>

        <div className="auth-reset-message">
          <div className="auth-reset-icon">
            <Mail size={22} aria-hidden="true" />
          </div>

          <div className="auth-form-header">
            <span className="auth-form-label">ACCOUNT SUPPORT</span>
            <h1 id="reset-heading">Forgot your password?</h1>
            <p>
              Password reset isn&apos;t available yet. No reset email has been
              sent. Please try again later or contact your site administrator
              for help accessing your account.
            </p>
          </div>
        </div>

        <div className="auth-register-prompt auth-reset-links">
          <Link to="/login">
            <ArrowLeft size={15} aria-hidden="true" />
            Back to Sign In
          </Link>
          <span>·</span>
          <Link to="/register">Create an account</Link>
        </div>
      </section>
    </main>
  );
}

export default ForgotPassword;
