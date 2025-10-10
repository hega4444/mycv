export interface User {
  email: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  email: string;
}

export interface PersonalData {
  full_name: string;
  job_title: string;
  email: string;
  phone: string;
  location: string;
  nationality: string;
  website: string;
  linkedin: string;
  github: string;
}

export interface CVContent {
  professional_summary: string;
  core_competencies: {
    technical_skills: string[];
  };
  professional_experience: ProfessionalExperience[];
  education: Education[];
  courses: Course[];
  key_projects: KeyProject[];
  languages: Language[];
}

export interface ProfessionalExperience {
  job_title: string;
  company: string;
  start_date: string;
  end_date: string;
  location: string;
  stack: string;
  achievements: string[];
}

export interface Education {
  degree: string;
  institution: string;
  location: string;
  start_year: string;
  graduation_year: string;
  details?: string;
}

export interface Course {
  name: string;
  provider: string;
  location: string;
  year: string;
  description: string;
}

export interface KeyProject {
  name: string;
  period: string;
  description: string;
  technologies: string[];
  details: string;
}

export interface Language {
  language: string;
  proficiency: string;
}

export interface Profile {
  personal_data: PersonalData;
  cv_content: CVContent;
}

export interface CV {
  id: string;
  description: string;
  job_description: string;
  link: string | null;
  model: string;
  provider: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  cv_optimized: CVContent | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface Settings {
  provider: string;
  model: string;
  api_key_display: string | null;
  has_api_key: boolean;
}

export interface Provider {
  id: string;
  name: string;
  models: Model[];
}

export interface Model {
  id: string;
  name: string;
}
