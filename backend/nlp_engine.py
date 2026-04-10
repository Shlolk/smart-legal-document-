"""
NLP Engine for Legal Rights Analysis
Uses transformers and semantic search to match complaints to constitutional rights
Falls back to keyword matching if transformers not available
"""

try:
    from transformers import pipeline
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️  Transformers not installed. Using keyword-based matching (install with: pip install -r requirements.txt)")

import json

# Legal Knowledge Base
LEGAL_KNOWLEDGE_BASE = {
    "police_search": {
        "keywords": ["police", "search", "warrant", "property", "vehicle", "phone", "seizure"],
        "issue_type": "Unlawful Search and Seizure",
        "constitutional_rights": "Fourth Amendment",
        "explanation": "The Fourth Amendment protects citizens against unreasonable searches and seizures. Law enforcement generally requires a valid warrant signed by a judge to search your property, vehicle, or person. A warrant must be based on probable cause—reasonable belief that a crime has been committed.",
        "civic_actions": [
            "Document the search: date, time, location, officers' names and badge numbers",
            "Ask if you're being detained or if free to leave",
            "Do not consent to searches without a warrant",
            "Request a copy of the search warrant",
            "Contact a lawyer immediately",
            "File a complaint with the police internal affairs division",
            "Consider filing a motion to suppress evidence if criminal charges are filed"
        ]
    },
    "wage_dispute": {
        "keywords": ["salary", "wage", "pay", "overtime", "payment", "employer", "work"],
        "issue_type": "Wage and Hour Violation",
        "constitutional_rights": "Economic Rights / Fair Labor Standards",
        "explanation": "The Fair Labor Standards Act (FLSA) is a federal law that requires employers to pay at least the minimum wage and overtime pay for hours worked over 40 per week. Employers must also maintain accurate records of hours worked. Violations can result in penalties and lawsuits.",
        "civic_actions": [
            "Gather all pay stubs and employment contracts",
            "Calculate total unpaid wages or overtime",
            "Keep detailed records of hours worked",
            "Report to your state's Department of Labor",
            "File with the Federal Department of Labor",
            "Consult with an employment lawyer about filing a claim",
            "Consider joining a class action lawsuit if multiple employees are affected"
        ]
    },
    "harassment": {
        "keywords": ["harassment", "bullying", "threat", "intimidation", "abuse", "assault"],
        "issue_type": "Harassment and Discrimination",
        "constitutional_rights": "Fourteenth Amendment (Equal Protection)",
        "explanation": "Harassment based on race, color, religion, sex, national origin, age, or disability is illegal under federal law. This includes workplace harassment, housing discrimination, and educational discrimination. Title VII, Fair Housing Act, and ADA provide protections.",
        "civic_actions": [
            "Document all incidents: date, time, witnesses, what was said/done",
            "Save all written communications (emails, texts, messages)",
            "Report to HR or management in writing",
            "File a complaint with the EEOC (Equal Employment Opportunity Commission)",
            "Keep copies of all complaint filings",
            "Interview potential witnesses",
            "Consult with an employment or civil rights attorney"
        ]
    },
    "eviction": {
        "keywords": ["eviction", "evict", "landlord", "rent", "housing", "lease", "tenant"],
        "issue_type": "Tenant Rights / Unlawful Eviction",
        "constitutional_rights": "Due Process Rights (Fifth Amendment)",
        "explanation": "Landlords must follow legal eviction procedures and cannot evict tenants without proper notice and court proceedings. Evictions for retaliation, discrimination, or without cause are illegal. Tenants have rights to habitability and protection from wrongful eviction.",
        "civic_actions": [
            "Respond to eviction notice within required time (usually 3-7 days)",
            "File answer in court if served with eviction lawsuit",
            "Gather evidence of habitability issues or retaliation",
            "Request continuance if you need time to prepare",
            "Contact legal aid organization for free representation",
            "Explore alternatives: mediation, payment plans",
            "Consult a tenant rights attorney"
        ]
    },
    "police_brutality": {
        "keywords": ["police", "brutal", "violence", "force", "injury", "excessive", "abuse"],
        "issue_type": "Police Brutality / Excessive Force",
        "constitutional_rights": "Eighth Amendment (Cruel and Unusual Punishment)",
        "explanation": "Officers are prohibited from using excessive force when making arrests or during encounters. Force must be proportional to the threat. Victims of police brutality can sue for civil rights violations, file criminal complaints, and seek damages.",
        "civic_actions": [
            "Seek immediate medical treatment and document injuries with photos",
            "Get names and badge numbers of all officers involved",
            "Request police incident report number",
            "Interview and get contact information from witnesses",
            "File complaint with police department's Internal Affairs",
            "File complaint with state Attorney General",
            "Contact civil rights organizations",
            "Consult a civil rights attorney about filing a lawsuit"
        ]
    },
    "free_speech": {
        "keywords": ["speech", "protest", "assembly", "expression", "arrest", "demonstration"],
        "issue_type": "First Amendment Rights Violation",
        "constitutional_rights": "First Amendment (Free Speech and Assembly)",
        "explanation": "The First Amendment protects freedom of speech, press, assembly, and petition. The government cannot arrest or punish you for peaceful speech or protest. Some exceptions exist: incitement to violence, true threats, or immediate physical danger.",
        "civic_actions": [
            "Document the incident: date, location, what you were saying/doing",
            "Get contact information from witnesses and observers",
            "Record the interaction if legal in your jurisdiction",
            "Request the police incident report",
            "File complaint with ACLU (American Civil Liberties Union)",
            "Preserve all evidence and communication",
            "Consult a constitutional rights attorney"
        ]
    },
    "disability_rights": {
        "keywords": ["disability", "accommodation", "ada", "disabled", "access", "reasonable"],
        "issue_type": "ADA Violation / Disability Discrimination",
        "constitutional_rights": "Americans with Disabilities Act (ADA)",
        "explanation": "The ADA prohibits discrimination against people with disabilities in employment, public services, public transportation, and telecommunications. Employers and public entities must provide reasonable accommodations.",
        "civic_actions": [
            "Document your disability and requested accommodation",
            "Request accommodation in writing to employer/organization",
            "Keep copies of all requests and responses",
            "File complaint with Department of Justice Civil Rights Division",
            "Report to state disability rights agency",
            "Request mediation/resolution meeting",
            "Consult with disability rights attorney if needed"
        ]
    }
}

TRANSLATION_MAP = {
    "hi-IN": {
        "police_search": {
            "issue_type": "अन्यायपूर्ण तलाशी और जब्ती",
            "constitutional_rights": "चौथा संशोधन",
            "explanation": "चौथा संशोधन नागरिकों को unreasonable तलाशी और जब्ती से सुरक्षा देता है। कानून प्रवर्तन को आमतौर पर आपकी संपत्ति, वाहन या व्यक्ति की तलाशी के लिए जज द्वारा जारी किए गए वॉरंट की आवश्यकता होती है। वॉरंट को संभावित कारण पर आधारित होना चाहिए।",
            "civic_actions": [
                "तलाशी का दस्तावेज़ीकरण करें: दिनांक, समय, स्थान, अधिकारी का नाम और बैज नंबर",
                "पूछें कि क्या आप हिरासत में हैं या आप जा सकते हैं",
                "बिना वॉरंट के तलाशी के लिए सहमति न दें",
                "तलाशी वॉरंट की प्रति का अनुरोध करें",
                "तुरंत एक वकील से संपर्क करें",
                "पुलिस आंतरिक मामलों के प्रभाग में शिकायत दर्ज करें",
                "यदि आपराधिक आरोप लगाए जा रहे हैं तो सबूत दबाने की गति पर विचार करें"
            ]
        },
        "wage_dispute": {
            "issue_type": "वेतन और घंटे का उल्लंघन",
            "constitutional_rights": "आर्थिक अधिकार / फेयर लेबर स्टैंडर्ड्स",
            "explanation": "फेयर लेबर स्टैंडर्ड्स एक्ट (FLSA) एक संघीय कानून है जो नियोक्ताओं को कम से कम न्यूनतम वेतन और 40 घंटे से अधिक काम के लिए ओवरटाइम भुगतान करने की आवश्यकता देता है। नियोक्ताओं को काम के घंटों का सटीक रिकॉर्ड भी रखना चाहिए। उल्लंघन दंड और मुकदमों का कारण बन सकते हैं।",
            "civic_actions": [
                "सभी वेतन पर्चियां और रोजगार अनुबंध एकत्र करें",
                "कुल बकाया वेतन या ओवरटाइम की गणना करें",
                "काम किए गए घंटों के विस्तृत रिकॉर्ड रखें",
                "अपने राज्य के श्रम विभाग को रिपोर्ट करें",
                "फेडरल डिपार्टमेंट ऑफ लेबर के साथ शिकायत दर्ज करें",
                "दावा दर्ज करने के लिए रोजगार वकील से परामर्श करें",
                "यदि कई कर्मचारियों को प्रभावित किया गया है तो समूह मुकदमे पर विचार करें"
            ]
        },
        "harassment": {
            "issue_type": "उत्पीड़न और भेदभाव",
            "constitutional_rights": "14वां संशोधन (समान संरक्षण)",
            "explanation": "जाति, रंग, धर्म, सेक्शुअल ओरिएंटेशन, राष्ट्रीय मूल, उम्र, या विकलांगता के आधार पर उत्पीड़न संघीय कानून के तहत अवैध है। इसमें कार्यस्थल उत्पीड़न, आवास भेदभाव और शैक्षिक भेदभाव शामिल हैं।",
            "civic_actions": [
                "सभी घटनाओं का दस्तावेजीकरण करें: दिनांक, समय, गवाह, क्या कहा/किया गया",
                "सभी लिखित संचार (ईमेल, टेक्स्ट, संदेश) सहेजें",
                "HR या प्रबंधन को लिखित रूप में रिपोर्ट करें",
                "EEOC (इक्वल इम्प्लॉयमेंट ऑपर्चुनिटी कमीशन) में शिकायत दर्ज करें",
                "सभी शिकायत दाखिल करने की प्रतियाँ रखें",
                "संभावित गवाहों का साक्षात्कार लें",
                "रोजगार या नागरिक अधिकार वकील से परामर्श करें"
            ]
        },
        "eviction": {
            "issue_type": "किरायेदार अधिकार / अवैध निकासी",
            "constitutional_rights": "न्यायिक प्रक्रिया अधिकार (पांचवां संशोधन)",
            "explanation": "मकान मालिकों को कानूनी निकासी प्रक्रियाओं का पालन करना चाहिए और उचित नोटिस और न्याय प्रक्रिया के बिना किरायेदारों को निकाल नहीं सकते। प्रतिशोध, भेदभाव, या बिना कारण निकासी अवैध है।",
            "civic_actions": [
                "आवश्यक समय के भीतर निकासी सूचना का जवाब दें (आम तौर पर 3-7 दिन)",
                "यदि आपको निकासी मुकदमा दिया गया है तो कोर्ट में उत्तर दाखिल करें",
                "विरोध या प्रतिशोध के सबूत एकत्र करें",
                "अगर आपको तैयारी के लिए समय चाहिए तो निरंतरता का अनुरोध करें",
                "मुफ्त प्रतिनिधित्व के लिए कानूनी सहायता संगठन से संपर्क करें",
                "विकल्पों का पता लगाएं: मध्यस्थता, भुगतान योजनाएं",
                "एक किरायेदार अधिकार वकील से परामर्श करें"
            ]
        },
        "police_brutality": {
            "issue_type": "पुलिस निर्ममता / अत्यधिक बल",
            "constitutional_rights": "आठवां संशोधन (क्रूर और असामान्य दंड)",
            "explanation": "अधिकारी गिरफ्तारी या मुठभेड़ के दौरान अत्यधिक बल का उपयोग नहीं कर सकते। बल को खतरे के अनुपात में होना चाहिए। पुलिस निर्ममता के पीड़ित नागरिक अधिकार हनन के लिए मुकदमा कर सकते हैं, आपराधिक शिकायत दर्ज कर सकते हैं, और हर्जाना मांग सकते हैं।",
            "civic_actions": [
                "तुरंत चिकित्सा उपचार लें और चोटों का फोटो के साथ दस्तावेजीकरण करें",
                "शामिल सभी अधिकारियों के नाम और बैज नंबर प्राप्त करें",
                "पुलिस घटना रिपोर्ट नंबर का अनुरोध करें",
                "गवाहों से संपर्क जानकारी प्राप्त करें",
                "पुलिस विभाग के आंतरिक मामलों के साथ शिकायत दर्ज करें",
                "राज्य के अटॉर्नी जनरल के साथ शिकायत दर्ज करें",
                "नागरिक अधिकार संगठनों से संपर्क करें",
                "एक नागरिक अधिकार वकील से परामर्श करें"
            ]
        },
        "free_speech": {
            "issue_type": "पहला संशोधन अधिकार उल्लंघन",
            "constitutional_rights": "पहला संशोधन (मुक्त भाषण और सभा)",
            "explanation": "पहला संशोधन भाषण, प्रेस, सभा, और याचिका की स्वतंत्रता की रक्षा करता है। सरकार शांतिपूर्ण भाषण या विरोध करने के लिए आपको गिरफ्तार या दंडित नहीं कर सकती। कुछ अपवाद हैं: हिंसा प्रोत्साहन, वास्तविक धमकियाँ, या तत्काल शारीरिक खतरा।",
            "civic_actions": [
                "घटना का दस्तावेजीकरण करें: दिनांक, स्थान, आप क्या कह रहे/कर रहे थे",
                "गवाहों और दर्शकों से संपर्क जानकारी प्राप्त करें",
                "अगर यह कानूनी है तो बातचीत को रिकॉर्ड करें",
                "पुलिस घटना रिपोर्ट का अनुरोध करें",
                "ACLU (अमेरिकन सिविल लिबर्टीज यूनियन) के साथ शिकायत दर्ज करें",
                "सभी साक्ष्य और संचार को सुरक्षित रखें",
                "एक संवैधानिक अधिकार वकील से परामर्श करें"
            ]
        },
        "disability_rights": {
            "issue_type": "ADA उल्लंघन / विकलांगता भेदभाव",
            "constitutional_rights": "अमेरिकन्स विद डिसेबिलिटीज एक्ट (ADA)",
            "explanation": "ADA सार्वजनिक सेवाओं, रोजगार, सार्वजनिक परिवहन और दूरसंचार में विकलांग लोगों के खिलाफ भेदभाव पर रोक लगाती है। नियोक्ताओं और सार्वजनिक संस्थाओं को उचित सुविधा प्रदान करनी चाहिए।",
            "civic_actions": [
                "अपनी विकलांगता और अनुरोधित सुविधा का दस्तावेजीकरण करें",
                "नियोक्ता/संगठन को लिखित में सुविधा का अनुरोध करें",
                "सभी अनुरोधों और प्रतिक्रियाओं की प्रतियाँ रखें",
                "न्याय विभाग नागरिक अधिकार विभाग के साथ शिकायत दर्ज करें",
                "राज्य विकलांगता अधिकार एजेंसी को रिपोर्ट करें",
                "मध्यस्थता/समाधान बैठक का अनुरोध करें",
                "आवश्यक होने पर एक विकलांगता अधिकार वकील से परामर्श करें"
            ]
        }
    },
    "es-ES": {
        "police_search": {
            "issue_type": "Registro y confiscación ilegales",
            "constitutional_rights": "Cuarta Enmienda",
            "explanation": "La Cuarta Enmienda protege a los ciudadanos contra registros y detenciones irrazonables. La policía normalmente necesita una orden válida firmada por un juez para registrar su propiedad, vehículo o persona. Una orden debe basarse en causa probable.",
            "civic_actions": [
                "Documente la búsqueda: fecha, hora, ubicación, nombres y números de placa de los agentes",
                "Pregunte si está detenido o si puede irse",
                "No consienta búsquedas sin una orden",
                "Solicite una copia de la orden de registro",
                "Contacte a un abogado inmediatamente",
                "Presente una queja ante la división de asuntos internos de la policía",
                "Considere presentar una moción para suprimir pruebas si se presentan cargos penales"
            ]
        },
        "wage_dispute": {
            "issue_type": "Violación de salario y horas",
            "constitutional_rights": "Derechos económicos / FLSA",
            "explanation": "La Ley de Normas Laborales Justas (FLSA) es una ley federal que exige a los empleadores pagar al menos el salario mínimo y el pago por horas extra por más de 40 horas trabajadas por semana. Los empleadores también deben mantener registros precisos de las horas trabajadas.",
            "civic_actions": [
                "Reúna todos los recibos de pago y contratos de empleo",
                "Calcule el salario o las horas extra no pagadas",
                "Mantenga registros detallados de las horas trabajadas",
                "Informe al Departamento de Trabajo de su estado",
                "Presente una queja al Departamento de Trabajo federal",
                "Consulte con un abogado laboral para presentar una demanda",
                "Considere una demanda colectiva si varios empleados están afectados"
            ]
        },
        "harassment": {
            "issue_type": "Acoso y discriminación",
            "constitutional_rights": "Decimocuarta Enmienda (Igualdad de protección)",
            "explanation": "El acoso basado en raza, color, religión, sexo, origen nacional, edad o discapacidad es ilegal según la ley federal. Esto incluye acoso en el lugar de trabajo, discriminación en viviendas y discriminación educativa.",
            "civic_actions": [
                "Documente todos los incidentes: fecha, hora, testigos, lo que se dijo/hizo",
                "Guarde todas las comunicaciones por escrito (correos, mensajes)",
                "Informe a Recursos Humanos o a la gerencia por escrito",
                "Presente una queja ante la EEOC",
                "Mantenga copias de todas las quejas presentadas",
                "Entrevise a posibles testigos",
                "Consulte con un abogado laboral o de derechos civiles"
            ]
        },
        "eviction": {
            "issue_type": "Derechos del inquilino / Desalojo ilegal",
            "constitutional_rights": "Derechos de debido proceso (Quinta Enmienda)",
            "explanation": "Los propietarios deben seguir procedimientos de desalojo legales y no pueden desalojar a los inquilinos sin aviso e intervención judicial. Los desalojos por represalia, discriminación o sin causa son ilegales.",
            "civic_actions": [
                "Responda al aviso de desalojo dentro del tiempo requerido",
                "Presente una respuesta en la corte si se le notifica un juicio de desalojo",
                "Reúna evidencia de problemas de habitabilidad o represalia",
                "Solicite una prórroga si necesita tiempo para prepararse",
                "Contacte a una organización de ayuda legal gratuita",
                "Explore alternativas: mediación, planes de pago",
                "Consulte con un abogado de derechos de inquilinos"
            ]
        },
        "police_brutality": {
            "issue_type": "Brutalidad policial / Fuerza excesiva",
            "constitutional_rights": "Octava Enmienda (Castigo cruel e inusual)",
            "explanation": "Los oficiales tienen prohibido usar fuerza excesiva al efectuar arrestos o durante encuentros. La fuerza debe ser proporcional a la amenaza. Las víctimas pueden demandar por violaciones de derechos civiles, presentar quejas penales y buscar daños.",
            "civic_actions": [
                "Busque atención médica inmediata y documente lesiones con fotos",
                "Obtenga nombres y números de placa de todos los oficiales involucrados",
                "Solicite el número de informe de incidente policial",
                "Entrevise y obtenga información de contacto de testigos",
                "Presente una queja en Asuntos Internos de la policía",
                "Presente una queja ante el Fiscal General del estado",
                "Contacte a organizaciones de derechos civiles",
                "Consulte a un abogado de derechos civiles"
            ]
        },
        "free_speech": {
            "issue_type": "Violación de derechos de libre expresión",
            "constitutional_rights": "Primera Enmienda (Libre expresión y reunión)",
            "explanation": "La Primera Enmienda protege la libertad de expresión, prensa, reunión y petición. El gobierno no puede arrestarlo ni castigarlo por discurso pacífico o protesta, salvo excepciones como incitación a violencia.",
            "civic_actions": [
                "Documente el incidente: fecha, ubicación, qué estaba diciendo/haciendo",
                "Obtenga información de contacto de testigos y observadores",
                "Grabe la interacción si es legal en su jurisdicción",
                "Solicite el informe de incidente policial",
                "Presente una queja ante la ACLU",
                "Conserve todas las pruebas y comunicaciones",
                "Consulte a un abogado de derechos constitucionales"
            ]
        },
        "disability_rights": {
            "issue_type": "Violación de la ADA / Discriminación por discapacidad",
            "constitutional_rights": "Ley de Estadounidenses con Discapacidades (ADA)",
            "explanation": "La ADA prohíbe la discriminación contra personas con discapacidades en el empleo, servicios públicos, transporte público y telecomunicaciones. Los empleadores y entidades públicas deben proporcionar adaptaciones razonables.",
            "civic_actions": [
                "Documente su discapacidad y la adaptación solicitada",
                "Solicite la adaptación por escrito al empleador/organización",
                "Guarde copias de todas las solicitudes y respuestas",
                "Presente una queja en la División de Derechos Civiles del Departamento de Justicia",
                "Informe a la agencia estatal de derechos de discapacidad",
                "Solicite mediación o reunión de resolución",
                "Consulte a un abogado de derechos de discapacidad si es necesario"
            ]
        }
    },
    "fr-FR": {
        "police_search": {
            "issue_type": "Perquisition et saisie illégales",
            "constitutional_rights": "Quatrième amendement",
            "explanation": "Le quatrième amendement protège les citoyens contre les perquisitions et saisies déraisonnables. Les forces de l'ordre ont généralement besoin d'un mandat valide signé par un juge pour perquisitionner votre propriété, véhicule ou personne. Le mandat doit être basé sur une cause probable.",
            "civic_actions": [
                "Documentez la perquisition : date, heure, lieu, noms et numéros de badge des agents",
                "Demandez si vous êtes en détention ou libre de partir",
                "Ne consentez pas à une perquisition sans mandat",
                "Demandez une copie du mandat de perquisition",
                "Contactez un avocat immédiatement",
                "Déposez une plainte auprès de la division des affaires internes de la police",
                "Envisagez de déposer une requête pour exclure les preuves si des accusations pénales sont portées"
            ]
        },
        "wage_dispute": {
            "issue_type": "Violation des salaires et heures",
            "constitutional_rights": "Droits économiques / FLSA",
            "explanation": "La Fair Labor Standards Act (FLSA) est une loi fédérale qui exige des employeurs qu'ils paient au moins le salaire minimum et les heures supplémentaires pour les heures travaillées au-delà de 40 heures par semaine. Les employeurs doivent également tenir des registres précis des heures travaillées.",
            "civic_actions": [
                "Rassemblez toutes les fiches de paie et contrats de travail",
                "Calculez le salaire ou les heures supplémentaires non payées",
                "Conservez des enregistrements détaillés des heures travaillées",
                "Signalez-le au département du travail de votre état",
                "Déposez une plainte auprès du département du travail fédéral",
                "Consultez un avocat spécialisé en droit du travail",
                "Envisagez une action collective si plusieurs employés sont concernés"
            ]
        },
        "harassment": {
            "issue_type": "Harcèlement et discrimination",
            "constitutional_rights": "Quatorzième amendement (égalité de protection)",
            "explanation": "Le harcèlement fondé sur la race, la couleur, la religion, le sexe, l'origine nationale, l'âge ou le handicap est illégal selon la loi fédérale. Cela inclut le harcèlement en milieu de travail, la discrimination au logement et la discrimination dans l'éducation.",
            "civic_actions": [
                "Documentez tous les incidents : date, heure, témoins, ce qui a été dit/fait",
                "Conservez toutes les communications écrites (e-mails, textos, messages)",
                "Signalez-le au service des ressources humaines ou à la direction par écrit",
                "Déposez une plainte auprès de l'EEOC",
                "Conservez des copies de toutes les plaintes déposées",
                "Interrogez les témoins potentiels",
                "Consultez un avocat en droit du travail ou en droits civiques"
            ]
        },
        "eviction": {
            "issue_type": "Droits du locataire / Expulsion illégale",
            "constitutional_rights": "Droits de procédure régulière (cinquième amendement)",
            "explanation": "Les propriétaires doivent suivre des procédures d'expulsion légales et ne peuvent pas expulser les locataires sans préavis approprié et procédure judiciaire. Les expulsions pour représailles, discrimination ou sans motif sont illégales.",
            "civic_actions": [
                "Répondez à l'avis d'expulsion dans le délai requis",
                "Déposez une réponse au tribunal si vous êtes assigné à une audience d'expulsion",
                "Rassemblez des preuves de problèmes d'habitabilité ou de représailles",
                "Demandez un report si vous avez besoin de temps pour vous préparer",
                "Contactez une organisation d'aide juridique gratuite",
                "Explorez des alternatives : médiation, plans de paiement",
                "Consultez un avocat des droits des locataires"
            ]
        },
        "police_brutality": {
            "issue_type": "Brutalité policière / Usage excessif de la force",
            "constitutional_rights": "Huitième amendement (peine cruelle et inhabituelle)",
            "explanation": "Les agents ne peuvent pas utiliser une force excessive lors d'arrestations ou d'interactions. La force doit être proportionnelle à la menace. Les victimes peuvent poursuivre pour violation des droits civils, déposer des plaintes pénales et demander des dommages-intérêts.",
            "civic_actions": [
                "Cherchez des soins médicaux immédiats et documentez les blessures avec des photos",
                "Obtenez les noms et numéros de badge de tous les agents impliqués",
                "Demandez le numéro de rapport d'incident policier",
                "Interrogez et obtenez les coordonnées des témoins",
                "Déposez une plainte auprès des affaires internes de la police",
                "Déposez une plainte auprès du procureur général de l'État",
                "Contactez des organisations de droits civils",
                "Consultez un avocat des droits civils"
            ]
        },
        "free_speech": {
            "issue_type": "Violation du droit à la liberté d'expression",
            "constitutional_rights": "Premier amendement (liberté d'expression et de rassemblement)",
            "explanation": "Le premier amendement protège la liberté d'expression, de la presse, de réunion et de pétition. Le gouvernement ne peut pas vous arrêter ou vous punir pour un discours pacifique ou une protestation, sauf exceptions comme l'incitation à la violence.",
            "civic_actions": [
                "Documentez l'incident : date, lieu, ce que vous disiez/faisiez",
                "Obtenez les coordonnées des témoins et observateurs",
                "Enregistrez l'interaction si c'est légal dans votre juridiction",
                "Demandez le rapport d'incident policier",
                "Déposez une plainte auprès de l'ACLU",
                "Conservez toutes les preuves et communications",
                "Consultez un avocat spécialisé en droits constitutionnels"
            ]
        },
        "disability_rights": {
            "issue_type": "Violation de l'ADA / Discrimination envers les personnes handicapées",
            "constitutional_rights": "Americans with Disabilities Act (ADA)",
            "explanation": "L'ADA interdit la discrimination à l'égard des personnes handicapées dans l'emploi, les services publics, les transports publics et les télécommunications. Les employeurs et entités publiques doivent fournir des aménagements raisonnables.",
            "civic_actions": [
                "Documentez votre handicap et l'aménagement demandé",
                "Demandez l'aménagement par écrit à l'employeur/organisation",
                "Conservez des copies de toutes les demandes et réponses",
                "Déposez une plainte auprès de la Division des droits civils du département de la Justice",
                "Signalez-le à l'agence d'État des droits des personnes handicapées",
                "Demandez une médiation ou une réunion de résolution",
                "Consultez un avocat en droits des personnes handicapées si nécessaire"
            ]
        }
    },
    "bn-IN": {
        "police_search": {
            "issue_type": "অবৈধ তল্লাশি এবং জব্দ",
            "constitutional_rights": "চতুর্থ সংশোধনী",
            "explanation": "চতুর্থ সংশোধনী নাগরিকদের অযৌক্তিক তল্লাশি এবং জব্দ থেকে রক্ষা করে। পুলিশকে সাধারণত আপনার সম্পত্তি, গাড়ি বা ব্যক্তির তল্লাশি করার জন্য একজন বিচারকের স্বাক্ষরিত বৈধ ওয়ারেন্ট প্রয়োজন। একটি ওয়ারেন্টকে সম্ভাব্য কারণের উপর ভিত্তি করতে হবে।",
            "civic_actions": [
                "তল্লাশি নথিভুক্ত করুন: তারিখ, সময়, অবস্থান, অফিসারদের নাম এবং ব্যাজ নম্বর",
                "জিজ্ঞাসা করুন যে আপনি গ্রেপ্তার হচ্ছেন কিনা বা যেতে পারেন কিনা",
                "ওয়ারেন্ট ছাড়া তল্লাশিতে সম্মতি দেবেন না",
                "তল্লাশি ওয়ারেন্টের একটি অনুলিপি অনুরোধ করুন",
                "অবিলম্বে একজন আইনজীবীর সাথে যোগাযোগ করুন",
                "পুলিশের অভ্যন্তরীণ বিষয়ক বিভাগে অভিযোগ দায়ের করুন",
                "যদি অপরাধমূলক অভিযোগ আনা হয় তাহলে প্রমাণ দমনের আবেদন বিবেচনা করুন"
            ]
        },
        "wage_dispute": {
            "issue_type": "বেতন এবং ঘণ্টা লঙ্ঘন",
            "constitutional_rights": "অর্থনৈতিক অধিকার / FLSA",
            "explanation": "ফেয়ার লেবার স্ট্যান্ডার্ডস অ্যাক্ট (FLSA) একটি ফেডারেল আইন যা নিয়োগকর্তাদের কমপক্ষে ন্যূনতম বেতন এবং সপ্তাহে 40 ঘণ্টার বেশি কাজের জন্য ওভারটাইম বেতন প্রদান করার প্রয়োজন করে। নিয়োগকর্তাদের কাজের ঘণ্টার সঠিক রেকর্ডও রাখতে হবে।",
            "civic_actions": [
                "সমস্ত বেতন পে-স্টাব এবং কর্মসংস্থান চুক্তি সংগ্রহ করুন",
                "মোট অবৈতনিক বেতন বা ওভারটাইম গণনা করুন",
                "কাজের ঘণ্টার বিস্তারিত রেকর্ড রাখুন",
                "আপনার রাজ্যের শ্রম বিভাগে রিপোর্ট করুন",
                "ফেডারেল শ্রম বিভাগে অভিযোগ দায়ের করুন",
                "দাবি দায়েরের জন্য একজন কর্মসংস্থান আইনজীবীর সাথে পরামর্শ করুন",
                "যদি একাধিক কর্মচারী প্রভাবিত হয় তাহলে ক্লাস অ্যাকশন বিবেচনা করুন"
            ]
        },
        "harassment": {
            "issue_type": "উত্যক্ত এবং বৈষম্য",
            "constitutional_rights": "চতুর্দশ সংশোধনী (সমান সুরক্ষা)",
            "explanation": "জাতি, বর্ণ, ধর্ম, লিঙ্গ, জাতীয় উত্স, বয়স বা প্রতিবন্ধকতার ভিত্তিতে উত্যক্ত ফেডারেল আইন অনুসারে অবৈধ। এতে কর্মক্ষেত্র উত্যক্ত, আবাসন বৈষম্য এবং শিক্ষাগত বৈষম্য অন্তর্ভুক্ত।",
            "civic_actions": [
                "সমস্ত ঘটনা নথিভুক্ত করুন: তারিখ, সময়, সাক্ষী, কী বলা/করা হয়েছে",
                "সমস্ত লিখিত যোগাযোগ (ইমেল, টেক্সট, বার্তা) সংরক্ষণ করুন",
                "HR বা ব্যবস্থাপনায় লিখিতভাবে রিপোর্ট করুন",
                "EEOC (ইকুয়াল এমপ্লয়মেন্ট অপরচুনিটি কমিশন) এ অভিযোগ দায়ের করুন",
                "সমস্ত অভিযোগ দাখিলের অনুলিপি রাখুন",
                "সম্ভাব্য সাক্ষীদের সাক্ষাত্কার নিন",
                "কর্মসংস্থান বা নাগরিক অধিকার আইনজীবীর সাথে পরামর্শ করুন"
            ]
        },
        "eviction": {
            "issue_type": "ভাড়াটিয়া অধিকার / অবৈধ উচ্ছেদ",
            "constitutional_rights": "ন্যায়সঙ্গত প্রক্রিয়া অধিকার (পঞ্চম সংশোধনী)",
            "explanation": "মালিকদের আইনি উচ্ছেদ প্রক্রিয়া অনুসরণ করতে হবে এবং উপযুক্ত নোটিশ এবং আদালত প্রক্রিয়া ছাড়া ভাড়াটিয়াদের উচ্ছেদ করতে পারবেন না। প্রতিশোধ, বৈষম্য বা কারণ ছাড়া উচ্ছেদ অবৈধ।",
            "civic_actions": [
                "প্রয়োজনীয় সময়ের মধ্যে উচ্ছেদ নোটিশের উত্তর দিন (সাধারণত 3-7 দিন)",
                "যদি উচ্ছেদ মামলা দেওয়া হয় তাহলে আদালতে উত্তর দাখিল করুন",
                "বাসযোগ্যতা সমস্যা বা প্রতিশোধের প্রমাণ সংগ্রহ করুন",
                "যদি প্রস্তুতির জন্য সময় প্রয়োজন হয় তাহলে স্থগিতকরণ অনুরোধ করুন",
                "বিনামূল্যে প্রতিনিধিত্বের জন্য আইনি সহায়তা সংস্থার সাথে যোগাযোগ করুন",
                "বিকল্পগুলি অন্বেষণ করুন: মধ্যস্থতা, অর্থ প্রদান পরিকল্পনা",
                "একজন ভাড়াটিয়া অধিকার আইনজীবীর সাথে পরামর্শ করুন"
            ]
        },
        "police_brutality": {
            "issue_type": "পুলিশ নির্যাতন / অতিরিক্ত বল",
            "constitutional_rights": "অষ্টম সংশোধনী (নিষ্ঠুর এবং অস্বাভাবিক শাস্তি)",
            "explanation": "অফিসাররা গ্রেপ্তার বা মুখোমুখি হওয়ার সময় অতিরিক্ত বল ব্যবহার করতে পারবেন না। বলকে হুমকির সাথে আনুপাতিক হতে হবে। পুলিশ নির্যাতনের শিকাররা নাগরিক অধিকার লঙ্ঘনের জন্য মামলা করতে পারেন, অপরাধমূলক অভিযোগ দায়ের করতে পারেন এবং ক্ষতিপূরণ দাবি করতে পারেন।",
            "civic_actions": [
                "অবিলম্বে চিকিৎসা সেবা নিন এবং আঘাতগুলি ফটো দিয়ে নথিভুক্ত করুন",
                "সমস্ত জড়িত অফিসারদের নাম এবং ব্যাজ নম্বর পান",
                "পুলিশ ঘটনা রিপোর্ট নম্বর অনুরোধ করুন",
                "সাক্ষীদের সাক্ষাত্কার নিন এবং যোগাযোগের তথ্য পান",
                "পুলিশ বিভাগের অভ্যন্তরীণ বিষয়ক বিভাগে অভিযোগ দায়ের করুন",
                "রাজ্যের অ্যাটর্নি জেনারেলের কাছে অভিযোগ দায়ের করুন",
                "নাগরিক অধিকার সংস্থার সাথে যোগাযোগ করুন",
                "নাগরিক অধিকার আইনজীবীর সাথে পরামর্শ করুন"
            ]
        },
        "free_speech": {
            "issue_type": "প্রথম সংশোধনী অধিকার লঙ্ঘন",
            "constitutional_rights": "প্রথম সংশোধনী (মুক্ত বাকস্বাধীনতা এবং সমাবেশ)",
            "explanation": "প্রথম সংশোধনী বাকস্বাধীনতা, প্রেস, সমাবেশ এবং আবেদনের স্বাধীনতা রক্ষা করে। সরকার শান্তিপূর্ণ বাক্য বা প্রতিবাদের জন্য আপনাকে গ্রেপ্তার বা শাস্তি দিতে পারে না। কিছু ব্যতিক্রম রয়েছে: সহিংসতা প্ররোচনা, সত্যিকারের হুমকি বা অবিলম্বে শারীরিক বিপদ।",
            "civic_actions": [
                "ঘটনা নথিভুক্ত করুন: তারিখ, অবস্থান, আপনি কী বলছিলেন/করছিলেন",
                "সাক্ষী এবং পর্যবেক্ষকদের যোগাযোগের তথ্য পান",
                "যদি আপনার এখতিয়ারে আইনি হয় তাহলে মিথস্ক্রিয়া রেকর্ড করুন",
                "পুলিশ ঘটনা রিপোর্ট অনুরোধ করুন",
                "ACLU (আমেরিকান সিভিল লিবার্টিজ ইউনিয়ন) এ অভিযোগ দায়ের করুন",
                "সমস্ত প্রমাণ এবং যোগাযোগ সংরক্ষণ করুন",
                "একজন সাংবিধানিক অধিকার আইনজীবীর সাথে পরামর্শ করুন"
            ]
        },
        "disability_rights": {
            "issue_type": "ADA লঙ্ঘন / প্রতিবন্ধকতা বৈষম্য",
            "constitutional_rights": "আমেরিকানস উইথ ডিসেবিলিটিজ অ্যাক্ট (ADA)",
            "explanation": "ADA কর্মসংস্থান, সরকারি পরিষেবা, সরকারি পরিবহন এবং টেলিযোগাযোগে প্রতিবন্ধকতা সম্পন্ন ব্যক্তিদের বিরুদ্ধে বৈষম্য নিষিদ্ধ করে। নিয়োগকর্তা এবং সরকারি সংস্থাগুলিকে যুক্তিসঙ্গত সুবিধা প্রদান করতে হবে।",
            "civic_actions": [
                "আপনার প্রতিবন্ধকতা এবং অনুরোধিত সুবিধা নথিভুক্ত করুন",
                "নিয়োগকর্তা/সংস্থায় লিখিতভাবে সুবিধা অনুরোধ করুন",
                "সমস্ত অনুরোধ এবং প্রতিক্রিয়ার অনুলিপি রাখুন",
                "ন্যায় বিভাগের নাগরিক অধিকার বিভাগে অভিযোগ দায়ের করুন",
                "রাজ্য প্রতিবন্ধকতা অধিকার সংস্থায় রিপোর্ট করুন",
                "মধ্যস্থতা/সমাধান সভা অনুরোধ করুন",
                "প্রয়োজনে একজন প্রতিবন্ধকতা অধিকার আইনজীবীর সাথে পরামর্শ করুন"
            ]
        }
    },
    "ta-IN": {
        "police_search": {
            "issue_type": "சட்டவிரோத தேடல் மற்றும் பறிமுதல்",
            "constitutional_rights": "நான்காவது திருத்தம்",
            "explanation": "நான்காவது திருத்தம் குடிமக்களை நியாயமற்ற தேடல் மற்றும் பறிமுதல்களில் இருந்து பாதுகாக்கிறது. காவல்துறைக்கு உங்கள் சொத்து, வாகனம் அல்லது நபரைத் தேடுவதற்கு ஒரு நீதிபதியால் கையொப்பமிடப்பட்ட சட்டப்பூர்வ வாரண்ட் தேவைப்படுகிறது. ஒரு வாரண்ட் சாத்தியமான காரணத்தின் அடிப்படையில் இருக்க வேண்டும்.",
            "civic_actions": [
                "தேடலை ஆவணப்படுத்துங்கள்: தேதி, நேரம், இடம், அதிகாரிகளின் பெயர்கள் மற்றும் பேட்ஜ் எண்கள்",
                "நீங்கள் கைது செய்யப்படுகிறீர்களா அல்லது செல்லலாமா என்று கேளுங்கள்",
                "வாரண்ட் இல்லாமல் தேடல்களுக்கு ஒப்புதல் அளிக்காதீர்கள்",
                "தேடல் வாரண்டின் நகலை கோருங்கள்",
                "உடனடியாக ஒரு வழக்கறிஞரைத் தொடர்பு கொள்ளுங்கள்",
                "காவல்துறை உள் விவகாரத் துறையில் புகார் செய்யுங்கள்",
                "குற்றச்சாட்டுகள் செய்யப்பட்டால் ஆதாரங்களை ஒடுக்குவதற்கான மனுவை கருதுங்கள்"
            ]
        },
        "wage_dispute": {
            "issue_type": "சம்பளம் மற்றும் மணிநேர மீறல்",
            "constitutional_rights": "பொருளாதார உரிமைகள் / FLSA",
            "explanation": "நியாயமான தொழிலாளர் தரநிலைகள் சட்டம் (FLSA) ஒரு கூட்டாட்சி சட்டம், இது முதலாளிகளுக்கு குறைந்தபட்ச சம்பளம் மற்றும் வாரத்திற்கு 40 மணிநேரத்திற்கு மேல் வேலைக்கான மேல்நேர சம்பளம் வழங்க வேண்டும். முதலாளிகள் வேலை மணிநேரங்களின் சரியான பதிவுகளையும் வைத்திருக்க வேண்டும்.",
            "civic_actions": [
                "அனைத்து சம்பள ஸ்டப்களையும் வேலைவாய்ப்பு ஒப்பந்தங்களையும் சேகரிக்கவும்",
                "மொத்த செலுத்தப்படாத சம்பளம் அல்லது மேல்நேரத்தை கணக்கிடுங்கள்",
                "வேலை மணிநேரங்களின் விரிவான பதிவுகளை வைத்திருங்கள்",
                "உங்கள் மாநில தொழிலாளர் துறையில் புகார் செய்யுங்கள்",
                "கூட்டாட்சி தொழிலாளர் துறையில் புகார் செய்யுங்கள்",
                "கோரிக்கை செய்வதற்கான வேலைவாய்ப்பு வழக்கறிஞரை அணுகுங்கள்",
                "பல ஊழியர்கள் பாதிக்கப்பட்டால் வகுப்பு நடவடிக்கையை கருதுங்கள்"
            ]
        },
        "harassment": {
            "issue_type": "தொல்லை மற்றும் பாகுபாடு",
            "constitutional_rights": "பதினான்காவது திருத்தம் (சம உரிமை)",
            "explanation": "இனம், நிறம், மதம், பாலினம், தேசிய தோற்றம், வயது அல்லது இயலாமை ஆகியவற்றின் அடிப்படையில் தொல்லை கூட்டாட்சி சட்டத்தின்படி சட்டவிரோதமானது. இதில் பணியிட தொல்லை, வீட்டுவசதி பாகுபாடு மற்றும் கல்வி பாகுபாடு அடங்கும்.",
            "civic_actions": [
                "அனைத்து சம்பவங்களையும் ஆவணப்படுத்துங்கள்: தேதி, நேரம், சாட்சிகள், என்ன சொல்லப்பட்டது/செய்யப்பட்டது",
                "அனைத்து எழுத்து தொடர்புகளையும் (மின்னஞ்சல், உரை, செய்திகள்) சேமிக்கவும்",
                "HR அல்லது மேலாண்மைக்கு எழுத்தாக புகார் செய்யுங்கள்",
                "EEOC இல் புகார் செய்யுங்கள்",
                "அனைத்து புகார் தாக்கல் நகல்களையும் வைத்திருங்கள்",
                "சாத்தியமான சாட்சிகளை நேர்காணல் செய்யுங்கள்",
                "வேலைவாய்ப்பு அல்லது குடிமக்கள் உரிமை வழக்கறிஞரை அணுகுங்கள்"
            ]
        },
        "eviction": {
            "issue_type": "குடியிருப்பாளர் உரிமைகள் / சட்டவிரோத வெளியேற்றம்",
            "constitutional_rights": "நியாயமான நடைமுறை உரிமைகள் (ஐந்தாவது திருத்தம்)",
            "explanation": "உரிமையாளர்கள் சட்டப்பூர்வ வெளியேற்ற நடைமுறைகளை பின்பற்ற வேண்டும் மற்றும் சரியான அறிவிப்பு மற்றும் நீதிமன்ற நடைமுறை இல்லாமல் குடியிருப்பாளர்களை வெளியேற்ற முடியாது. பழிவாங்கல், பாகுபாடு அல்லது காரணம் இல்லாமல் வெளியேற்றங்கள் சட்டவிரோதமானவை.",
            "civic_actions": [
                "தேவையான நேரத்திற்குள் வெளியேற்ற அறிவிப்புக்கு பதிலளிக்கவும்",
                "வெளியேற்ற வழக்கு வழங்கப்பட்டால் நீதிமன்றத்தில் பதிலளிக்கவும்",
                "வசதி சிக்கல்கள் அல்லது பழிவாங்கலின் ஆதாரங்களை சேகரிக்கவும்",
                "தயார்படுத்துவதற்கு நேரம் தேவைப்பட்டால் தள்ளிப்போடலை கோருங்கள்",
                "இலவச பிரதிநிதித்துவத்திற்கான சட்ட உதவி அமைப்பைத் தொடர்பு கொள்ளுங்கள்",
                "மாற்றங்களை ஆராயுங்கள்: மத்தியஸ்தம், கட்டண திட்டங்கள்",
                "குடியிருப்பாளர் உரிமை வழக்கறிஞரை அணுகுங்கள்"
            ]
        },
        "police_brutality": {
            "issue_type": "காவல்துறை கொடூரம் / மிகை வலிமை",
            "constitutional_rights": "எட்டாவது திருத்தம் (கொடூரமான மற்றும் அசாதாரண தண்டனை)",
            "explanation": "அதிகாரிகள் கைது செய்யும் போது அல்லது எதிர்ப்புகளின் போது மிகை வலிமை பயன்படுத்த முடியாது. வலிமை அச்சுறுத்தலுக்கு தகுந்ததாக இருக்க வேண்டும். காவல்துறை கொடூரத்தின் பாதிப்புகள் குடிமக்கள் உரிமை மீறல்களுக்கு வழக்கு செய்யலாம், குற்ற புகார்களை செய்யலாம் மற்றும் இழப்பீடுகளை கோரலாம்.",
            "civic_actions": [
                "உடனடியாக மருத்துவ சிகிச்சை பெறுங்கள் மற்றும் காயங்களை புகைப்படங்களுடன் ஆவணப்படுத்துங்கள்",
                "அனைத்து ஈடுபட்ட அதிகாரிகளின் பெயர்கள் மற்றும் பேட்ஜ் எண்களைப் பெறுங்கள்",
                "காவல்துறை சம்பவ அறிக்கை எண்ணை கோருங்கள்",
                "சாட்சிகளை நேர்காணல் செய்து தொடர்பு தகவல்களைப் பெறுங்கள்",
                "காவல்துறை உள் விவகாரங்களில் புகார் செய்யுங்கள்",
                "மாநில அட்டர்னி ஜெனரலுக்கு புகார் செய்யுங்கள்",
                "குடிமக்கள் உரிமை அமைப்புகளைத் தொடர்பு கொள்ளுங்கள்",
                "குடிமக்கள் உரிமை வழக்கறிஞரை அணுகுங்கள்"
            ]
        },
        "free_speech": {
            "issue_type": "முதல் திருத்த உரிமை மீறல்",
            "constitutional_rights": "முதல் திருத்தம் (முதல் வாக்கு மற்றும் சபை)",
            "explanation": "முதல் திருத்தம் வாக்கு, செய்தித்தாள், சபை மற்றும் மனு உரிமைகளைப் பாதுகாக்கிறது. அரசு அமைதியான வாக்கு அல்லது எதிர்ப்புக்காக உங்களை கைது செய்ய முடியாது அல்லது தண்டிக்க முடியாது. சில விதிவிலக்குகள் உள்ளன: வன்முறை தூண்டுதல், உண்மையான அச்சுறுத்தல்கள் அல்லது உடனடியான உடல் ஆபத்து.",
            "civic_actions": [
                "சம்பவத்தை ஆவணப்படுத்துங்கள்: தேதி, இடம், நீங்கள் என்ன சொல்லிக்கொண்டிருந்தீர்கள்/செய்துகொண்டிருந்தீர்கள்",
                "சாட்சிகள் மற்றும் கண்காணிப்பாளர்களின் தொடர்பு தகவல்களைப் பெறுங்கள்",
                "உங்கள் அதிகார வரம்பில் சட்டப்பூர்வமாக இருந்தால் மி஥ஸ்கிரியாவை பதிவு செய்யுங்கள்",
                "காவல்துறை சம்பவ அறிக்கையை கோருங்கள்",
                "ACLU இல் புகார் செய்யுங்கள்",
                "அனைத்து ஆதாரங்கள் மற்றும் தொடர்புகளையும் பாதுகாப்பாக வைத்திருங்கள்",
                "ஒரு அரசியல் சாசன உரிமை வழக்கறிஞரை அணுகுங்கள்"
            ]
        },
        "disability_rights": {
            "issue_type": "ADA மீறல் / இயலாமை பாகுபாடு",
            "constitutional_rights": "அமெரிக்கர்கள் இயலாமை சட்டம் (ADA)",
            "explanation": "ADA வேலைவாய்ப்பு, பொது சேவைகள், பொது போக்குவரத்து மற்றும் தொலைதொடர்புகளில் இயலாமை உள்ளவர்களுக்கு எதிரான பாகுபாட்டை தடை செய்கிறது. முதலாளிகள் மற்றும் பொது அமைப்புகள் நியாயமான தகவமைப்புகளை வழங்க வேண்டும்.",
            "civic_actions": [
                "உங்கள் இயலாமை மற்றும் கோரப்பட்ட தகவமைப்பை ஆவணப்படுத்துங்கள்",
                "முதலாளி/அமைப்புக்கு எழுத்தாக தகவமைப்பு கோருங்கள்",
                "அனைத்து கோரிக்கைகள் மற்றும் பதில்களின் நகல்களையும் வைத்திருங்கள்",
                "நீதித்துறை குடிமக்கள் உரிமை பிரிவுக்கு புகார் செய்யுங்கள்",
                "மாநில இயலாமை உரிமை அமைப்புக்கு புகார் செய்யுங்கள்",
                "மத்தியஸ்தம்/தீர்வு கூட்டத்தை கோருங்கள்",
                "தேவைப்பட்டால் இயலாமை உரிமை வழக்கறிஞரை அணுகுங்கள்"
            ]
        }
    },
    "mr-IN": {
        "police_search": {
            "issue_type": "अवैध शोध आणि जप्ती",
            "constitutional_rights": "चौथी दुरुस्ती",
            "explanation": "चौथी दुरुस्ती नागरिकांना अनुचित शोध आणि जप्तीपासून संरक्षण देते. पोलिसांना तुमची मालमत्ता, वाहन किंवा व्यक्ती शोधण्यासाठी न्यायाधीशाने स्वाक्षरी केलेला वैध वॉरंट आवश्यक असतो. वॉरंटला संभाव्य कारणावर आधारित असणे आवश्यक आहे.",
            "civic_actions": [
                "शोध दस्तऐवजीकरण करा: तारीख, वेळ, स्थान, अधिकाऱ्यांचे नावे आणि बॅज क्रमांक",
                "तुम्हाला अटक होत आहे का किंवा जाऊ शकता का हे विचारा",
                "वॉरंटशिवाय शोधांना संमती देऊ नका",
                "शोध वॉरंटची प्रत मागवा",
                "तातडीने वकिलाशी संपर्क साधा",
                "पोलिसांच्या अंतर्गत व्यवहार विभागात तक्रार दाखल करा",
                "जर गुन्हेगारी आरोप केले जात असतील तर पुरावा दाबण्याची याचिका विचारात घ्या"
            ]
        },
        "wage_dispute": {
            "issue_type": "वेतन आणि तास उल्लंघन",
            "constitutional_rights": "आर्थिक हक्क / FLSA",
            "explanation": "निष्पक्ष श्रम मानके कायदा (FLSA) हा एक संघीय कायदा आहे जो नियोक्त्यांना किमान वेतन आणि आठवड्यात 40 तासांपेक्षा जास्त कामासाठी ओव्हरटाइम वेतन देणे आवश्यक करतो. नियोक्त्यांनी कामाच्या तासांची अचूक नोंद ठेवणे आवश्यक आहे.",
            "civic_actions": [
                "सर्व वेतन पावत्या आणि रोजगार करार गोळा करा",
                "एकूण न भरलेले वेतन किंवा ओव्हरटाइम गणना करा",
                "कामाच्या तासांची तपशीलवार नोंद ठेवा",
                "तुमच्या राज्याच्या श्रम विभागात तक्रार करा",
                "संघीय श्रम विभागात तक्रार दाखल करा",
                "दावा दाखल करण्यासाठी रोजगार वकिलाशी सल्लामसलत करा",
                "जर अनेक कर्मचारी प्रभावित झाले असतील तर वर्ग कारवाई विचारात घ्या"
            ]
        },
        "harassment": {
            "issue_type": "त्रास आणि भेदभाव",
            "constitutional_rights": "चौदावी दुरुस्ती (समान संरक्षण)",
            "explanation": "जात, रंग, धर्म, लिंग, राष्ट्रीय मूळ, वय किंवा अपंगत्वाच्या आधारावर त्रास देणे संघीय कायद्याने अवैध आहे. यामध्ये कार्यक्षेत्रातील त्रास, गृह भेदभाव आणि शैक्षणिक भेदभाव समाविष्ट आहे.",
            "civic_actions": [
                "सर्व घटना दस्तऐवजीकरण करा: तारीख, वेळ, साक्षीदार, काय सांगितले/केले गेले",
                "सर्व लिखित संवाद (ईमेल, मजकूर, संदेश) जतन करा",
                "HR किंवा व्यवस्थापनाला लिखित स्वरूपात तक्रार करा",
                "EEOC मध्ये तक्रार दाखल करा",
                "सर्व तक्रार दाखल केलेल्या नोंदी ठेवा",
                "संभाव्य साक्षीदारांची मुलाखत घ्या",
                "रोजगार किंवा नागरी हक्क वकिलाशी सल्लामसलत करा"
            ]
        },
        "eviction": {
            "issue_type": "भाडेकरू हक्क / अवैध हकालपट्टी",
            "constitutional_rights": "न्याय्य प्रक्रिया हक्क (पाचवी दुरुस्ती)",
            "explanation": "मालकांनी कायदेशीर हकालपट्टी प्रक्रिया पाळणे आवश्यक आहे आणि योग्य नोटीस आणि न्यायालयीन प्रक्रिया नसल्यास भाडेकरूंना हाकलू शकत नाहीत. प्रतिशोध, भेदभाव किंवा कारण नसल्यास हकालपट्टी अवैध आहे.",
            "civic_actions": [
                "आवश्यक वेळेत हकालपट्टी नोटीसला उत्तर द्या",
                "हकालपट्टी खटला दिल्यास न्यायालयात उत्तर दाखल करा",
                "वसाहत समस्यांचे किंवा प्रतिशोधाचे पुरावे गोळा करा",
                "तयारीसाठी वेळ हवा असल्यास स्थगिती मागवा",
                "विनामूल्य प्रतिनिधित्वासाठी कायदेशीर मदत संस्थेशी संपर्क साधा",
                "पर्यायांचा शोध घ्या: मध्यस्थी, देय योजना",
                "भाडेकरू हक्क वकिलाशी सल्लामसलत करा"
            ]
        },
        "police_brutality": {
            "issue_type": "पोलिस क्रूरता / अत्याधिक शक्ती",
            "constitutional_rights": "आठवी दुरुस्ती (क्रूर आणि असामान्य शिक्षा)",
            "explanation": "अधिकाऱ्यांना अटक करताना किंवा सामना करताना अत्याधिक शक्ती वापरण्यास मनाई आहे. शक्ती धोक्याच्या प्रमाणात असणे आवश्यक आहे. पोलिस क्रूरतेचे पीडित नागरी हक्क उल्लंघनासाठी खटले दाखल करू शकतात, गुन्हेगारी तक्रारी करू शकतात आणि नुकसान भरपाई मागू शकतात.",
            "civic_actions": [
                "तातडीने वैद्यकीय उपचार घ्या आणि जखमा फोटोने दस्तऐवजीकरण करा",
                "सर्व सहभागी अधिकाऱ्यांचे नावे आणि बॅज क्रमांक मिळवा",
                "पोलिस घटना अहवाल क्रमांक मागवा",
                "साक्षीदारांची मुलाखत घ्या आणि संपर्क माहिती मिळवा",
                "पोलिस विभागाच्या अंतर्गत व्यवहारात तक्रार दाखल करा",
                "राज्य अटर्नी जनरलकडे तक्रार दाखल करा",
                "नागरी हक्क संस्थांशी संपर्क साधा",
                "नागरी हक्क वकिलाशी सल्लामसलत करा"
            ]
        },
        "free_speech": {
            "issue_type": "पहिली दुरुस्ती हक्क उल्लंघन",
            "constitutional_rights": "पहिली दुरुस्ती (मुक्त भाषण आणि सभा)",
            "explanation": "पहिली दुरुस्ती भाषण, प्रसिद्धी माध्यम, सभा आणि याचनेची स्वातंत्र्ये संरक्षित करते. सरकार शांततापूर्ण भाषण किंवा विरोधासाठी तुम्हाला अटक करू शकत नाही किंवा शिक्षा करू शकत नाही. काही अपवाद आहेत: हिंसाचाराला प्रोत्साहन देणे, खरी धमकी किंवा तातडीची शारीरिक धोका.",
            "civic_actions": [
                "घटना दस्तऐवजीकरण करा: तारीख, स्थान, तुम्ही काय बोलत/करत होतात",
                "साक्षीदार आणि निरीक्षकांची संपर्क माहिती मिळवा",
                "तुमच्या अधिकारक्षेत्रात कायदेशीर असल्यास संवाद रेकॉर्ड करा",
                "पोलिस घटना अहवाल मागवा",
                "ACLU मध्ये तक्रार दाखल करा",
                "सर्व पुरावे आणि संवाद सुरक्षित ठेवा",
                "संविधानिक हक्क वकिलाशी सल्लामसलत करा"
            ]
        },
        "disability_rights": {
            "issue_type": "ADA उल्लंघन / अपंगत्व भेदभाव",
            "constitutional_rights": "अमेरिकन्स विथ डिसएबिलिटीज अॅक्ट (ADA)",
            "explanation": "ADA रोजगार, सार्वजनिक सेवा, सार्वजनिक वाहतूक आणि दूरसंचारात अपंगत्व असलेल्या व्यक्तींविरुद्ध भेदभाव करण्यास मनाई करते. नियोक्ते आणि सार्वजनिक संस्थांनी योग्य सुविधा प्रदान करणे आवश्यक आहे.",
            "civic_actions": [
                "तुमचे अपंगत्व आणि विनंती केलेली सुविधा दस्तऐवजीकरण करा",
                "नियोक्ता/संस्थेकडे लिखित स्वरूपात सुविधा मागवा",
                "सर्व विनंत्या आणि प्रतिसादांच्या प्रतिलिपी ठेवा",
                "न्याय विभाग नागरी हक्क विभागात तक्रार दाखल करा",
                "राज्य अपंगत्व हक्क संस्थेत तक्रार करा",
                "मध्यस्थी/निराकरण बैठक मागवा",
                "आवश्यक असल्यास अपंगत्व हक्क वकिलाशी सल्लामसलत करा"
            ]
        }
    }
}

class LegalNLPEngine:
    def __init__(self):
        """Initialize NLP models and knowledge base"""
        self.issue_keys = list(LEGAL_KNOWLEDGE_BASE.keys())
        self.classifier = None
        self.vectorizer = None
        self.issue_vectors = None
        
        if TRANSFORMERS_AVAILABLE:
            try:
                # Load zero-shot classification for issue type detection
                self.classifier = pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli"
                )
                
                # Prepare TF-IDF vectorizer for semantic search
                all_keywords = []
                
                for issue_key in self.issue_keys:
                    issue_data = LEGAL_KNOWLEDGE_BASE[issue_key]
                    all_keywords.append(" ".join(issue_data["keywords"]))
                
                self.vectorizer = TfidfVectorizer()
                self.issue_vectors = self.vectorizer.fit_transform(all_keywords)
            except Exception as e:
                print(f"⚠️  Failed to load transformers: {e}. Using fallback keyword matching.")
                self.classifier = None
                self.vectorizer = None
    
    def identify_issue(self, problem_text: str) -> str:
        """
        Identify the legal issue type from complaint text
        Returns the issue key from LEGAL_KNOWLEDGE_BASE
        """
        if self.vectorizer is None:
            # Fallback: keyword matching
            problem_lower = problem_text.lower()
            best_match = "wage_dispute"  # default
            max_matches = 0
            
            for issue_key, issue_data in LEGAL_KNOWLEDGE_BASE.items():
                keyword_matches = sum(1 for kw in issue_data["keywords"] if kw in problem_lower)
                if keyword_matches > max_matches:
                    max_matches = keyword_matches
                    best_match = issue_key
            
            return best_match
        
        # Create TF-IDF vector for the problem
        problem_vector = self.vectorizer.transform([problem_text])
        
        # Calculate similarity with all issues
        similarities = cosine_similarity(problem_vector, self.issue_vectors)[0]
        
        # Get the most similar issue
        best_match_idx = int(np.argmax(similarities))
        best_match_score = float(similarities[best_match_idx])
        
        # If similarity is too low, use zero-shot classification
        if best_match_score < 0.1 and self.classifier:
            try:
                issue_options = self.issue_keys
                result = self.classifier(
                    problem_text,
                    issue_options,
                    hypothesis_template="This is about {}."
                )
                return result["labels"][0]
            except:
                pass
        
        return self.issue_keys[best_match_idx]
    
    def _translate_issue_data(self, issue_key: str, language: str) -> dict:
        if language == "en-US":
            return {}
        return TRANSLATION_MAP.get(language, {}).get(issue_key, {})

    def analyze_problem(self, problem_text: str, language: str = "en-US") -> dict:
        """
        Complete analysis of a legal problem
        Returns all relevant information
        """
        # Identify the issue
        issue_key = self.identify_issue(problem_text)
        issue_data = LEGAL_KNOWLEDGE_BASE.get(issue_key, {})
        translated_data = self._translate_issue_data(issue_key, language)
        
        confidence = 0.85 if self.vectorizer is None else 0.95
        
        return {
            "issue_type": translated_data.get("issue_type", issue_data.get("issue_type", "Legal Issue")),
            "related_article_or_law": translated_data.get("constitutional_rights", issue_data.get("constitutional_rights", "Consult Attorney")),
            "simplified_explanation": translated_data.get("explanation", issue_data.get("explanation", "Please consult with a legal professional.")),
            "recommended_actions": translated_data.get("civic_actions", issue_data.get("civic_actions", [])),
            "confidence_score": confidence
        }

# Initialize engine
try:
    nlp_engine = LegalNLPEngine()
except Exception as e:
    print(f"Error initializing NLP engine: {e}")
    nlp_engine = None

def analyze_legal_problem(problem_text: str, language: str = "en-US") -> dict:
    """Public function to analyze legal problems"""
    if nlp_engine is None:
        return {
            "issue_type": "Unable to analyze",
            "related_article_or_law": "Please consult an attorney",
            "simplified_explanation": "The NLP engine failed to initialize. Please check the error logs.",
            "recommended_actions": ["Consult with a qualified attorney"],
            "confidence_score": 0.0
        }
    return nlp_engine.analyze_problem(problem_text, language=language)
