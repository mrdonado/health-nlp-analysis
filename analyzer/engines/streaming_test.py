import sys
import tweepy

access_token = "3581919021-mS6wdcsvSaecYc1uWYiXpewSxi7jFBJJKN9393U"
access_token_secret = "0fmE8JzbJwDrp3l5SBLSLhqzsYbiYHh0jNFhbJ1FFkVId"
consumer_key = "tVacHH2m7cuZ5T0iJFlfTUmaU"
consumer_secret = "2zADWfnbutDzZj8Sic2qfZA52hGQlPk59x4GAbzJatk2tC3vUK"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
####FUNCIONA PERO HAY QUE METER ESPACIO DELANTE Y DETRAS DE LA QUERY
queries = ["health", "healthcare", "biomedical", "biotech", "cardiovascular", "chronic", "clinical", "gastrointestinal", "healthier", "healthy", "hematologic", "hepatic", "immune", "infectious", "interventional", "med", "medic", "medical", "molecular", "neuromuscular", "palliative", "pediatric", "pharmaceutical", "preventive", "regenerative", "restorative", "therapeutic", "inflammatory", "parasitic", "viral", "blood", "bones", "brain", "circulation", "ear", "endocrine", "eye", "hair", "heart", "kidney", "lung", "muscles", "nervous", "pulmonary", "skin", "stomach", "throat", "renal", "cancer", "complications", "condition", "conditions", "disease", "diseases", "disorder", "disorders", "dysfunction", "dysfunctions", "HIV", "infection", "infections", "inflammation", "injuries", "injury", "pain", "problems", "syndrome", "syndromes", "tumor", "tumour", "addictions", "alzheimer", "asthma", "autoimmune", "defects", "complication", "dementia", "depression", "diabetes", "traumas", "failure", "hypertension", "influenza", "leukemia", "lymphoma", "sclerosis", "obesity", "osteoarthritis", "parkinson", "psoriasis", "arthritis", "schizophrenia", "stroke", "trauma", "tuberculosis", "aging", "allergy", "anatomical", "anatomy", "autoimmunity", "bio", "biochemistry", "bioengineering", "biology", "biopharma", "biosciences", "biostatistics", "biotechnology", "cardiology", "chesmistry", "dermatology", "digitalhealth", "echocardiography", "ehealth", "endocrinology", "epidemiology", "exercise medicine", "gastroenterology", "gene", "genetics", "genomics", "geriatrics", "gynecology", "hematology", "histology", "immunity", "immunology", "immunometabolism", "immunotherapy", "life science(s)", "medtech", "metabolism", "microbiology", "nanotechnology", "nephrology", "neuro-oncology", "neurology", "neuroscience", "neurosurgery", "nursing", "nutrition", "obstetrics", "oncology", "oncopathology", "ophthalmology", "parasitology", "pathology", "pediatrics", "pharma", "pharmacology", "physiology", "plastics", "pregnancy", "psychiatry", "radiology", "rheumatology", "science", "surgery", "toxicology", "vascular", "virology", "wellness", "cardiomyopathy", "legal", "gynecologic", "law", "immunization", "neonatology", "orthopedics", "otolaryngology", "reproductive", "urology", "forensic", "#health", "#healthcare", "breast cancer", "care", "cells", "cellular", "chemicals", "critical", "cure", "diagnose", "diagnosed", "diagnoses", "diagnosis", "diagnostic", "drug", "drugs", "health", "health care", "healthcare", "imaging", "life-saving", "lifestyle", "medication", "medications", "medicine", "patient", "patients", "prevent", "prevention", "prognosis", "rehabilitation", "research", "survivor", "symptoms", "therapeutics", "therapies", "therapy", "transplantations", "treat", "treatment", "treatments", "trials", "vaccines", "virus", "wellbeing", "diagnostics", "diet", "devices", "end-of-life", "insurance", "anaesthetist", "cardiologist", "dermatologist", "microbiologist", "nephrologist", "neurologist", "neurosurgeon", "ophthalmologist", "paediatrician", "pathologist", "physician", "radiologist", "surgeon", "urologist", "acupuncturist", "aidman", "allergist", "analyst", "anesthesiologist", "apothecary", "biologist", "biostatistician", "caregiver", "carer", "chemical engineering", "chiropodist", "chiropractic", "chiropractor", "clinician", "consultant", "coroner", "cytopathologist", "dentist", "dermatopathologist", "digestive", "doc", "doctor", "Dr.", "echocardiographer", "electrophysiologist", "EMT", "endodontics", "epidemiologist", "G.P.", "GP", "gynaecologist", "gynecologist", "health worker", "hematologist", "hematologyst", "hospitalist", "immunologist", "intensivist", "intern", "interne", "internist", "M.D.", "MD", "medstudent", "neuropathologist", "neuroradiologist", "nurse", "nurse-practitioner", "nutritionist", "ob-gyn", "obstetrician", "occupational therapist", "oncologist", "orthopaedist", "orthopedist", "osteopath", "pediatrician", "pediatrist", "pharmacist", "pharmacologist", "physiatrist", "physicians", "physicist", "physio", "physiologist", "physiotherapist", "podiatrist", "practitioner", "practitioners", "psychologist", "resident", "scientist", "social worker", "surgical", "therapist", "specialist", "urogynaecologist", "neonatologist", "geriatrician", "psychiatrist", "otolaryngologist", "expert", "anesthetist", "endocrinologist", "gastroenterologist", "hepatologist", "examiner", "geneticist", "perinatologist", "respirologist", "rheumatologist", "pubmed", "stemcells", "FDA", "hospital", "institute", "laboratoy"]

def analyze_the_user(user_name, user_description):
    from user_analyzer import user_name_parser
    from user_analyzer import dictionary_parser
    from user_analyzer import lexicon_generator
    from user_analyzer import user_analyzer
    USER_NAME_PATTERNS = user_name_parser('/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/user_name_patterns.txt')
    DICTIONARY = dictionary_parser('/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/user_dictionary.txt')
    LEXICON = lexicon_generator('/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/user_grammar.txt', DICTIONARY)
    result = user_analyzer(user_name, user_description, USER_NAME_PATTERNS, LEXICON)
    #0: pattern, 1:tag, 2:from user/description
    return result

def analyze_the_message(message):
    from text_analyzer import analyzer
    from text_analyzer import language_data_loader
    LANGUAGE_DATA = language_data_loader('/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/grammar.txt',
    '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/counter_grammar.txt',
    '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/start_words.txt', 
    '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/stop_words.txt')
    message = unicode(message)
    result = analyzer(message, LANGUAGE_DATA['start_words'], LANGUAGE_DATA['grammar'], LANGUAGE_DATA['counter_grammar'], LANGUAGE_DATA['stop_words'])
    #0: problem, 1:solution
    return result

def disease_finder(message):
    result = False
    diseases_file_name = '/Users/DoraDorita/Lifescope1Nov/health-nlp-analysis/language_data/start_words.txt'
    disease_file = open(diseases_file_name, 'r')
    for line in disease_file:
        disease = line.rstrip()
        if disease in message:
            result = True
            break
    return result

class CustomStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        if status.user.description is not None:
            for q in queries:
                if q in status.user.description:
                    if disease_finder(status.text) is True:
                        user_result = analyze_the_user(status.user.screen_name, status.user.description)
                        if user_result[1] != '<no tag>':
                            print '\n------------'
                            print user_result[1], ' *** ', status.user.description
                            message_result = analyze_the_message(status.text)
                            print '\n'
                            print message_result[0], '/', message_result[1], ' *** ', status.text
                            print '------------'
                        break
            #, status.user.location, status.user.description

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream

sapi = tweepy.streaming.Stream(auth, CustomStreamListener())
sapi.filter(track=queries, stall_warnings=True)
