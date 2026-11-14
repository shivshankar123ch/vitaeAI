import React from "react";
import {
  ArrowRight,
  BarChart3,
  BrainCircuit,
  BriefcaseBusiness,
  Code2,
  Database,
  Layers3,
  Palette,
  Search,
  Sparkles,
} from "lucide-react";
import { Link } from "react-router-dom";
import AtoZBrand from "./AtoZBrand";
import "./JobSeekerLanding.css";

const careerAreas = [
  { label: "AI / ML", icon: BrainCircuit },
  { label: "Data & Analytics", icon: BarChart3 },
  { label: "Data Engineering", icon: Database },
  { label: "Backend Development", icon: Layers3 },
  { label: "Frontend Development", icon: Code2 },
  { label: "Product & Design", icon: Palette },
];

const steps = [
  {
    number: "01",
    title: "Create your profile",
    description: "Tell us about your skills, education, and the work you want to do.",
    icon: Sparkles,
  },
  {
    number: "02",
    title: "Explore opportunities",
    description: "Find roles and hiring drives that fit your next career move.",
    icon: Search,
  },
  {
    number: "03",
    title: "Keep moving forward",
    description: "Apply and keep track of your opportunities in one place.",
    icon: BriefcaseBusiness,
  },
];

export default function JobSeekerLanding() {
  return (
    <main className="job-seeker-page">
      <header className="job-seeker-header">
        <div className="job-seeker-header__inner">
          <AtoZBrand />
          <nav className="job-seeker-header__actions" aria-label="Job seeker account">
            <Link className="job-seeker-button job-seeker-button--quiet" to="/login">
              Employee login
            </Link>
            <Link className="job-seeker-button job-seeker-button--primary" to="/register">
              Register as employee <ArrowRight size={16} aria-hidden="true" />
            </Link>
            <Link className="job-seeker-header__recruiter" to="/r_login">
              Recruiter login
            </Link>
          </nav>
        </div>
      </header>

      <section className="job-seeker-hero">
        <div className="job-seeker-hero__content">
          <span className="job-seeker-eyebrow">
            <Sparkles size={14} aria-hidden="true" />
            CAREERS, CURATED FOR YOU
          </span>
          <h1>Find work that fits your <span>future.</span></h1>
          <p>
            Discover opportunities, build your profile, and take your next career
            step with Vitae.
          </p>
          <div className="job-seeker-hero__actions">
            <Link className="job-seeker-button job-seeker-button--primary" to="/register">
              Register as employee <ArrowRight size={17} aria-hidden="true" />
            </Link>
            <Link className="job-seeker-button job-seeker-button--outline" to="/login">
              Employee login
            </Link>
          </div>
          <div className="job-seeker-hero__note">
            <span className="job-seeker-hero__note-dot" />
            Your next opportunity starts with one step.
          </div>
        </div>

        <div className="job-seeker-preview" aria-label="Vitae job seeker features">
          <div className="job-seeker-preview__topline">
            <span><i /> YOUR CAREER SPACE</span>
            <span>VITAE</span>
          </div>
          <div className="job-seeker-preview__welcome">
            <span>YOUR NEXT CHAPTER</span>
            <h2>Make room for<br />what’s next.</h2>
          </div>
          <div className="job-seeker-preview__search">
            <Search size={18} aria-hidden="true" />
            <span>Opportunities matched to your goals</span>
            <ArrowRight size={17} aria-hidden="true" />
          </div>
          <div className="job-seeker-preview__features">
            <div>
              <span className="job-seeker-preview__icon job-seeker-preview__icon--pink">
                <BriefcaseBusiness size={18} aria-hidden="true" />
              </span>
              <span><strong>Discover</strong><small>Explore opportunities</small></span>
              <ArrowRight size={16} aria-hidden="true" />
            </div>
            <div>
              <span className="job-seeker-preview__icon job-seeker-preview__icon--green">
                <BarChart3 size={18} aria-hidden="true" />
              </span>
              <span><strong>Move forward</strong><small>Keep your journey organised</small></span>
              <ArrowRight size={16} aria-hidden="true" />
            </div>
          </div>
        </div>
      </section>

      <section className="job-seeker-areas" aria-labelledby="job-seeker-areas-title">
        <div className="job-seeker-section-heading">
          <span>EXPLORE YOUR POSSIBILITIES</span>
          <h2 id="job-seeker-areas-title">Find your place in tech</h2>
          <p>Start with an area that sparks your interest.</p>
        </div>
        <div className="job-seeker-areas__grid">
          {careerAreas.map(({ label, icon: Icon }) => (
            <div className="job-seeker-area" key={label}>
              <Icon size={20} aria-hidden="true" />
              <span>{label}</span>
              <ArrowRight size={15} aria-hidden="true" />
            </div>
          ))}
        </div>
      </section>

      <section className="job-seeker-steps" aria-labelledby="job-seeker-steps-title">
        <div className="job-seeker-section-heading">
          <span>YOUR JOURNEY WITH VITAE</span>
          <h2 id="job-seeker-steps-title">A clearer path to your next role</h2>
        </div>
        <div className="job-seeker-steps__grid">
          {steps.map(({ number, title, description, icon: Icon }) => (
            <article className="job-seeker-step" key={number}>
              <div className="job-seeker-step__top">
                <span>{number}</span>
                <Icon size={20} aria-hidden="true" />
              </div>
              <h3>{title}</h3>
              <p>{description}</p>
            </article>
          ))}
        </div>
        <div className="job-seeker-final-cta">
          <div>
            <h2>Ready to take the next step?</h2>
            <p>Create your employee account or sign in to continue.</p>
          </div>
          <div className="job-seeker-final-cta__actions">
            <Link className="job-seeker-button job-seeker-button--primary" to="/register">
              Register as employee <ArrowRight size={16} aria-hidden="true" />
            </Link>
            <Link className="job-seeker-final-cta__login" to="/login">Employee login</Link>
          </div>
        </div>
      </section>
    </main>
  );
}
