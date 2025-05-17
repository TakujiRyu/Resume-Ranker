from flask import Flask, render_template, request, redirect, url_for, session
import spacy
from spacy.matcher import PhraseMatcher
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = "your_secret_key"  # needed for session

nlp = spacy.load("en_core_web_sm")

JOB_DESCRIPTIONS = {
    "Information Technology": "We are looking for a Data Scientist with 5+ years of experience in Python, machine learning, and data analysis. The candidate should be proficient in libraries such as pandas, scikit-learn, and TensorFlow. A Master's degree in Computer Science, Data Science, or related field is preferred. Familiarity with NLP and cloud platforms like AWS is a plus.",
    "Teacher": "We are seeking a qualified and passionate teacher with at least 3 years of experience in classroom instruction. The ideal candidate should have strong communication skills, expertise in lesson planning, and the ability to engage students across diverse learning levels. A Bachelor’s degree in Education or a relevant subject is required. Certification or experience in remote teaching methods is a plus.",
    "Engineering": "We are looking for an experienced engineer with 4+ years of hands-on experience in product development and design. The candidate should be proficient in CAD software, problem-solving, and project management. A Bachelor’s degree in Engineering (Mechanical, Electrical, Civil, or related field) is required. Experience with industry standards and regulatory compliance is highly desirable.",
    "HR": "Join our HR team to handle recruitment, employee relations, and organizational development. We seek a proactive HR professional with 3+ years of experience managing talent acquisition, onboarding, and HR policies. Strong interpersonal skills and familiarity with HRIS systems are essential. A Bachelor’s degree in Human Resources, Business Administration, or related discipline is preferred.",
    "Accountant": "We’re hiring an accountant with 3+ years of experience in financial reporting, bookkeeping, and tax compliance. The candidate should have strong knowledge of accounting principles and proficiency with accounting software such as QuickBooks or SAP. A Bachelor’s degree in Accounting or Finance is required. CPA certification is an advantage.",
    "Healthcare": "Looking for a healthcare provider with experience delivering patient-centered care in clinical settings. The ideal candidate will have relevant medical qualifications and certifications, strong communication skills, and the ability to work collaboratively within a multidisciplinary team. Experience in electronic medical records (EMR) systems and patient education is a plus."
}

PROFESSIONS = list(JOB_DESCRIPTIONS.keys())

SKILL_TERMS = [
    "python", "machine learning", "data science", "deep learning", "nlp",
    "computer vision", "statistics", "data analysis", "data visualization",
    "big data", "cloud computing", "sql", "java", "c++", "javascript"
]
EDUCATION_TERMS = [
    "bachelor", "master", "phd", "doctorate", "degree", "university", "college",
    "institute", "high school", "diploma"
]
EXPERIENCE_TERMS = ["experience", "years", "worked", "role", "project", "position", "responsibilities"]

def build_matcher(term_list, label):
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(term.lower()) for term in term_list]
    matcher.add(label, patterns)
    return matcher

def get_matches(matcher, doc):
    matches = matcher(doc)
    return list(set([doc[start:end].text for _, start, end in matches]))

SKILL_MATCHER = build_matcher(SKILL_TERMS, "SKILLS")
EDUCATION_MATCHER = build_matcher(EDUCATION_TERMS, "EDUCATION")

def extract_entities(text):
    doc = nlp(text.lower())
    skills = get_matches(SKILL_MATCHER, doc)
    education = get_matches(EDUCATION_MATCHER, doc)
    experience = [
        sent.text.strip()
        for sent in doc.sents
        if any(kw in sent.text.lower() for kw in EXPERIENCE_TERMS)
    ]
    if not skills:
        skills = ["No skills found"]
    if not education:
        education = ["No education found"]
    if not experience:
        experience = ["No experience found"]
    return {
        "SKILLS": skills,
        "EDUCATION": education,
        "EXPERIENCE": experience
    }

models = {
    "paraphrase-MiniLM-L12-v2": SentenceTransformer("paraphrase-MiniLM-L12-v2"),
}

profession_thresholds = {
    "Teacher": 0.60,
    "Engineering": 0.65,
    "HR": 0.58,
    "Accountant": 0.62,
    "Information Technology": 0.64,
    "Healthcare": 0.60
}

def read_pdf(file):
    try:
        reader = PdfReader(file)
        text = " ".join(page.extract_text() or "" for page in reader.pages)
        return text
    except:
        return ""

def clean_and_tokenize(text):
    doc = nlp(text)
    return " ".join(
        token.lemma_.lower()
        for token in doc
        if token.is_alpha and not token.is_stop
    )

def explain_similarity(resume_text, job_desc_text, model):
    resume_embedding = model.encode([resume_text])
    job_embedding = model.encode([job_desc_text])
    similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]
    similarity_category = "Low"
    if similarity >= 0.75:
        similarity_category = "High"
    elif similarity >= 0.5:
        similarity_category = "Medium"
    return {
        "similarity_score": round(similarity, 3),
        "similarity_category": similarity_category,
        "resume_preview": resume_text[:300],
        "job_desc_preview": job_desc_text[:300]
    }

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        profession = request.form.get("profession")
        if profession not in PROFESSIONS:
            return redirect(url_for("index"))
        return redirect(url_for("homepage", profession=profession))
    return render_template("index.html", professions=PROFESSIONS)

@app.route("/homepage", methods=["GET", "POST"])
def homepage():
    profession = session.get('profession')
    job_desc = session.get('job_description')
    if not profession or not job_desc:
        return redirect(url_for("index"))  # redirect back to start if no profession selected

    results = None
    best_resume_info = None

    if request.method == "POST":
        uploaded_files = request.files.getlist("resumes")
        if not uploaded_files or len(uploaded_files) == 0:
            return render_template("homepage.html", profession=profession, error="No resumes uploaded.")

        threshold = profession_thresholds.get(profession, 0.70)
        job_text = clean_and_tokenize(job_desc)

        model_results = {}
        for model_name, model in models.items():
            resume_scores = []
            for resume_file in uploaded_files:
                resume_text = read_pdf(resume_file)
                if not resume_text.strip():
                    continue
                resume_clean = clean_and_tokenize(resume_text)
                explanation = explain_similarity(resume_clean, job_text, model)
                entities = extract_entities(resume_text)
                skills = entities.get("SKILLS", [])
                education = entities.get("EDUCATION", [])
                experience_texts = entities.get("EXPERIENCE", [])
                passed = explanation["similarity_score"] >= threshold

                resume_scores.append({
                    "filename": resume_file.filename,
                    "similarity_score": explanation["similarity_score"],
                    "skills": skills,
                    "education": education,
                    "experience_texts": experience_texts,
                    "preview": explanation["resume_preview"],
                    "passed": passed
                })
            model_results[model_name] = sorted(resume_scores, key=lambda x: x["similarity_score"], reverse=True)

        

        # Pick best resume overall
        best_score = -1
        for resumes in model_results.values():
            if resumes:
                top_resume = resumes[0]
                if top_resume["similarity_score"] > best_score:
                    best_score = top_resume["similarity_score"]
                    best_resume_info = top_resume
                    best_resume_info["model"] = model_name

        results = model_results
        return render_template("homepage.html", profession=profession, results=results, best_resume=best_resume_info)

    # GET method
    profession = request.args.get("profession")
    if profession:
        # Save profession and job description in session
        if profession not in PROFESSIONS:
            return redirect(url_for("index"))
        
        session["profession"] = profession
        session["job_description"] = JOB_DESCRIPTIONS.get(profession, "")
    
    else:
        # If no query param profession, check session
        profession = session.get("profession")
        if not profession:
            return redirect(url_for("index"))
    
    return render_template("homepage.html", profession=profession)

if __name__ == "__main__":
    app.run(debug=True)
