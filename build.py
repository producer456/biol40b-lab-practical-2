#!/usr/bin/env python3
"""Builds the self-contained mock-practical HTML from images + question data."""
import base64, json, mimetypes, os, pathlib

BASE = pathlib.Path(__file__).parent
IMG = BASE / "images"
OUT = BASE / "practical.html"

# ---- image metadata ----
# crop = [cx,cy,cw,ch] in % of the original image: the central region shown
#        (cuts off the baked-in label margins). covers = extra rects [x,y,w,h] in
#        ORIGINAL % that hide any stray label sitting inside the crop.
IMAGES = {
    "heart_internal": {
        "file": "heart_internal.jpg",
        "caption": "Heart — frontal (coronal) section, anterior view",
        "crop": [23, 7, 52, 80], "covers": [],
    },
    "heart_surface_ant": {
        "file": "heart_surface.jpg",
        "caption": "Heart — external surface, anterior view",
        "crop": [34, 2, 42, 46], "covers": [[67,43,12,4]],
    },
    "heart_surface_post": {
        "file": "heart_surface.jpg",
        "caption": "Heart — external surface, posterior view",
        "crop": [34, 50, 41, 48], "covers": [[27,50,21,13]],
    },
    "heart_valves": {
        "file": "heart_valves.jpg",
        "caption": "Heart valves — superior view (atria removed)",
        "crop": [12, 15, 76, 63], "covers": [],
    },
    "heart_conduction": {
        "file": "heart_conduction.jpg",
        "caption": "Cardiac conduction system — anterior view of frontal section",
        "crop": [28, 4, 48, 90], "covers": [],
    },
    "blood_formed": {
        "file": "blood_formed.png",
        "caption": "Blood smear — formed elements (slide #16)",
        "crop": [0, 0, 100, 100],
        "covers": [[13,2,60,9],[3,39,29,8],[50,39,20,8],[3,87,31,9],
                   [6,76,19,8],[30,74,25,8],[58,64,19,8],[78,68,19,8],[67,86,20,8]],
    },
    "vessel_cutaway": {
        "file": "vessel_wall2.png",
        "caption": "Artery wall — layers (slide #3, Artery/Vein/Nerve)",
        "crop": [24, 44, 54, 52], "covers": [],
    },
    "vessel_cross": {
        "file": "vessel_wall2.png",
        "caption": "Artery — cross-section (slide #3)",
        "crop": [2, 7, 36, 38], "covers": [],
    },
    "cardiac_dia": {
        "file": "cardiac_dia.png",
        "caption": "Cardiac muscle — intercalated discs (slide #45)",
        "crop": [17, 53, 32, 45], "covers": [],
    },
    "cardiac_histo": {
        "file": "cardiac_histo.png",
        "caption": "Cardiac muscle — histology (slide #45)",
        "crop": [3, 5, 90, 90], "covers": [],
    },
    "heart_wall": {
        "file": "heart_wall.jpg",
        "caption": "Heart wall & pericardium — layered detail",
        "crop": [31, 40, 41, 58], "covers": [],
    },
    # ---- respiratory (Lab 8) ----
    "resp_overview": {
        "file": "resp_overview.jpg",
        "caption": "Respiratory system — overview",
        "crop": [16, 10, 42, 85], "covers": [],
    },
    "resp_upper": {
        "file": "resp_upper.jpg",
        "caption": "Upper airway — nasal cavity & pharynx (sagittal section)",
        "crop": [15, 3, 46, 94], "covers": [],
    },
    "resp_larynx": {
        "file": "resp_larynx.jpg",
        "caption": "Larynx — anterior view",
        "crop": [33, 0, 30, 41], "covers": [[50, 0, 13, 41]],
    },
    "resp_lungs": {
        "file": "resp_lungs.jpg",
        "caption": "Lungs — lobes & bronchial tree",
        "crop": [9, 1, 72, 89], "covers": [],
    },
    "resp_alveoli": {
        "file": "resp_alveoli.png",
        "caption": "Alveoli — lung histology",
        "crop": [28, 6, 58, 66], "covers": [],
    },
    "resp_trachea_histo": {
        "file": "resp_trachea_histo.jpg",
        "caption": "Trachea wall — histology (slide #9)",
        "crop": [1, 15, 78, 73], "covers": [],
    },
    "resp_pleura": {
        "file": "resp_pleura.jpg",
        "caption": "Pleural membranes (detail)",
        "crop": [67, 15, 31, 35], "covers": [],
    },
    "resp_muscles": {
        "file": "resp_pleura.jpg",
        "caption": "Respiratory muscles — thoracic cavity",
        "crop": [10, 8, 40, 84], "covers": [[30, 12, 13, 5], [32, 59, 16, 5]],
    },
}

D, O = "Deoxygenated", "Oxygenated"

# ---- questions: img, x, y (% of image), name, accepted answers, function, blood ----
Q = [
 # ===== Station A: heart_internal =====
 ("heart_internal",44,11,"Aorta (ascending)",["aorta","ascending aorta"],
  "Receives oxygenated blood from the left ventricle and carries it to the systemic circulation.",O),
 ("heart_internal",35,11,"Superior vena cava",["superior vena cava","svc"],
  "Returns deoxygenated blood from the head, neck, and upper limbs to the right atrium.",D),
 ("heart_internal",44,24,"Pulmonary trunk",["pulmonary trunk"],
  "Carries deoxygenated blood from the right ventricle toward the lungs; splits into the L and R pulmonary arteries.",D),
 ("heart_internal",29,33,"Right pulmonary veins",["right pulmonary veins","pulmonary veins","right pulmonary vein"],
  "Return oxygenated blood from the right lung to the left atrium.",O),
 ("heart_internal",37,42,"Right atrium",["right atrium"],
  "Receives deoxygenated blood from the venae cavae and coronary sinus, then pumps it to the right ventricle.",D),
 ("heart_internal",41,52,"Tricuspid valve",["tricuspid valve","tricuspid","right atrioventricular valve","right av valve"],
  "Right AV valve; prevents backflow from the right ventricle into the right atrium during ventricular contraction.",D),
 ("heart_internal",33,58,"Right ventricle",["right ventricle"],
  "Pumps deoxygenated blood into the pulmonary trunk to the lungs.",D),
 ("heart_internal",47,56,"Chordae tendineae",["chordae tendineae","chordae tendinae","chordae"],
  "Fibrous cords that anchor the AV-valve cusps to the papillary muscles, preventing valve prolapse.",None),
 ("heart_internal",41,66,"Trabeculae carneae",["trabeculae carneae","trabeculae carnae"],
  "Muscular ridges on the internal walls of the ventricles.",None),
 ("heart_internal",34,80,"Inferior vena cava",["inferior vena cava","ivc"],
  "Returns deoxygenated blood from the trunk and lower limbs to the right atrium.",D),
 ("heart_internal",58,19,"Left pulmonary artery",["left pulmonary artery"],
  "Carries deoxygenated blood from the pulmonary trunk to the left lung.",D),
 ("heart_internal",34,19,"Right pulmonary artery",["right pulmonary artery"],
  "Carries deoxygenated blood from the pulmonary trunk to the right lung.",D),
 ("heart_internal",62,30,"Left atrium",["left atrium"],
  "Receives oxygenated blood from the pulmonary veins and pumps it to the left ventricle.",O),
 ("heart_internal",67,33,"Left pulmonary veins",["left pulmonary veins","left pulmonary vein"],
  "Return oxygenated blood from the left lung to the left atrium.",O),
 ("heart_internal",60,40,"Bicuspid (mitral) valve",["bicuspid valve","mitral valve","bicuspid","mitral","left atrioventricular valve","left av valve"],
  "Left AV valve; prevents backflow from the left ventricle into the left atrium.",O),
 ("heart_internal",66,55,"Left ventricle",["left ventricle"],
  "Pumps oxygenated blood into the aorta for systemic circulation; thickest-walled chamber.",O),
 ("heart_internal",58,61,"Papillary muscle",["papillary muscle","papillary muscles"],
  "Contracts to tension the chordae tendineae, keeping the AV valves closed during ventricular systole.",None),
 ("heart_internal",52,63,"Interventricular septum",["interventricular septum","iv septum","ventricular septum"],
  "Muscular wall that separates the right and left ventricles.",None),
 ("heart_internal",73,66,"Epicardium",["epicardium","visceral pericardium"],
  "Outermost layer of the heart wall (the visceral pericardium).",None),
 ("heart_internal",70,72,"Myocardium",["myocardium"],
  "Thick middle layer of cardiac muscle responsible for the heart's contraction.",None),
 ("heart_internal",68,77,"Endocardium",["endocardium"],
  "Smooth inner endothelial lining of the heart chambers and valves.",None),
 # ===== Station 2: heart_surface_ant (anterior) =====
 ("heart_surface_ant",40,16,"Ascending aorta",["ascending aorta","aorta"],
  "Carries oxygenated blood from the left ventricle to the body; gives rise to the coronary arteries.",O),
 ("heart_surface_ant",54,9,"Aortic arch",["aortic arch","arch of aorta","arch of the aorta"],
  "Curve of the aorta that gives off the brachiocephalic, left common carotid, and left subclavian arteries.",O),
 ("heart_surface_ant",53,15,"Ligamentum arteriosum",["ligamentum arteriosum"],
  "Fetal remnant of the ductus arteriosus, connecting the pulmonary trunk to the aortic arch.",None),
 ("heart_surface_ant",58,20,"Auricle of left atrium",["auricle of left atrium","left auricle"],
  "Ear-like flap that increases the volume capacity of the left atrium.",O),
 ("heart_surface_ant",36,20,"Right auricle",["right auricle","auricle of right atrium"],
  "Ear-like extension that increases the capacity of the right atrium.",D),
 ("heart_surface_ant",54,26,"Left coronary artery",["left coronary artery"],
  "Supplies oxygenated blood to the left side of the heart; branches into the circumflex and anterior interventricular arteries.",O),
 ("heart_surface_ant",37,27,"Right coronary artery",["right coronary artery"],
  "Supplies oxygenated blood to the right side of the heart.",O),
 ("heart_surface_ant",54,36,"Anterior interventricular artery",["anterior interventricular artery","lad","left anterior descending artery"],
  "Runs in the anterior interventricular groove supplying both ventricles and the septum (the 'LAD').",O),
 ("heart_surface_ant",56,33,"Great cardiac vein",["great cardiac vein"],
  "Collects deoxygenated blood from the anterior heart and empties into the coronary sinus.",D),
 ("heart_surface_ant",52,45,"Apex of heart",["apex","apex of heart","apex of the heart"],
  "Inferior pointed tip of the heart, formed by the left ventricle.",None),
 # ===== Station 3: heart_surface_post (posterior) =====
 ("heart_surface_post",52,74,"Coronary sinus",["coronary sinus"],
  "Large vein on the posterior heart that drains cardiac (deoxygenated) blood into the right atrium.",D),
 ("heart_surface_post",48,86,"Middle cardiac vein",["middle cardiac vein"],
  "Drains the posterior heart and empties into the coronary sinus.",D),
 ("heart_surface_post",50,83,"Posterior interventricular artery",["posterior interventricular artery"],
  "Branch of the right coronary artery supplying the posterior walls of the ventricles.",O),
 # ===== Station C: heart_valves =====
 ("heart_valves",30,27,"Tricuspid valve",["tricuspid valve","tricuspid","right atrioventricular valve","right av valve"],
  "Right AV valve; three cusps; prevents backflow from the right ventricle into the right atrium.",D),
 ("heart_valves",62,25,"Bicuspid (mitral) valve",["bicuspid valve","mitral valve","bicuspid","mitral","left atrioventricular valve","left av valve"],
  "Left AV valve; two cusps; prevents backflow from the left ventricle into the left atrium.",O),
 ("heart_valves",45,52,"Aortic semilunar valve",["aortic valve","aortic semilunar valve","aortic"],
  "Three half-moon cusps; prevents backflow from the aorta into the left ventricle.",O),
 ("heart_valves",47,73,"Pulmonary semilunar valve",["pulmonary valve","pulmonary semilunar valve"],
  "Three cusps; prevents backflow from the pulmonary trunk into the right ventricle.",D),
 # ===== Station D: heart_conduction =====
 ("heart_conduction",39,33,"Sinoatrial (SA) node",["sinoatrial node","sa node","sinoatrial (sa) node","pacemaker"],
  "The heart's pacemaker; initiates each heartbeat and sets the heart rate (in the right atrial wall).",None),
 ("heart_conduction",41,49,"Atrioventricular (AV) node",["atrioventricular node","av node","atrioventricular (av) node"],
  "Delays the impulse before it reaches the ventricles, letting the atria finish contracting first.",None),
 ("heart_conduction",48,53,"Atrioventricular bundle (bundle of His)",["atrioventricular bundle","bundle of his","av bundle","bundle of his (atrioventricular bundle)"],
  "Carries the impulse from the AV node into the interventricular septum; the only electrical link between atria and ventricles.",None),
 ("heart_conduction",55,66,"Right and left bundle branches",["bundle branches","right and left bundle branches","av bundle branches"],
  "Conduct the impulse down either side of the interventricular septum toward the apex.",None),
 ("heart_conduction",58,78,"Purkinje fibers",["purkinje fibers","purkinje fibres","purkinje"],
  "Distribute the impulse through the ventricular myocardium, triggering ventricular contraction.",None),
 # ===== Station 6: blood_formed (slide 16) =====
 ("blood_formed",28,22,"Erythrocytes",["erythrocytes","erythrocyte","red blood cells","red blood cell","rbc","rbcs"],
  "Carry oxygen (and some carbon dioxide) throughout the body using hemoglobin.",None),
 ("blood_formed",72,20,"Platelets",["platelets","platelet","thrombocytes","thrombocyte"],
  "Cell fragments that clot blood and stop bleeding (hemostasis).",None),
 ("blood_formed",15,60,"Monocyte",["monocyte","monocytes"],
  "Largest WBC; leaves the blood to become a macrophage that phagocytizes pathogens and debris.",None),
 ("blood_formed",40,62,"Lymphocyte",["lymphocyte","lymphocytes"],
  "WBC of specific immunity — B cells make antibodies, T cells attack infected cells.",None),
 ("blood_formed",68,55,"Eosinophil",["eosinophil","eosinophils"],
  "Granular WBC that fights parasitic worms and moderates allergic and inflammatory responses.",None),
 ("blood_formed",87,55,"Basophil",["basophil","basophils"],
  "Granular WBC that releases histamine (inflammation) and heparin (anticoagulant) during allergic responses.",None),
 ("blood_formed",77,78,"Neutrophil",["neutrophil","neutrophils"],
  "Most abundant WBC; a first-responder that phagocytizes bacteria.",None),
 # ===== Station 7: vessel_cutaway (slide 3) =====
 ("vessel_cutaway",32,66,"Tunica externa",["tunica externa","tunica adventitia","externa","adventitia"],
  "Outermost vessel layer of connective tissue that anchors and protects the vessel.",None),
 ("vessel_cutaway",46,66,"Tunica media",["tunica media","media"],
  "Middle layer of smooth muscle and elastic tissue that controls vessel diameter (constriction/dilation).",None),
 ("vessel_cutaway",66,71,"Internal elastic lamina",["internal elastic lamina","internal elastic membrane"],
  "Sheet of elastic tissue between the tunica interna and tunica media.",None),
 ("vessel_cutaway",73,60,"Endothelium",["endothelium"],
  "Simple squamous epithelium lining the lumen; gives a smooth, low-friction surface for blood flow.",None),
 # ===== Station 8: vessel_cross (slide 3) =====
 ("vessel_cross",26,31,"Lumen",["lumen"],
  "The hollow central channel of the vessel through which blood flows.",None),
 ("vessel_cross",25,40,"Tunica interna (intima)",["tunica interna","tunica intima","intima","interna"],
  "Innermost layer lining the lumen; made of endothelium on a thin connective-tissue layer.",None),
 # ===== Station 9: cardiac_dia (slide 45) =====
 ("cardiac_dia",38,71,"Intercalated disc",["intercalated disc","intercalated discs","intercalated disk"],
  "Junction between cardiac muscle cells; its gap junctions let the cells contract in unison.",None),
 ("cardiac_dia",24,68,"Myofiber",["myofiber","cardiac muscle cell","cardiac muscle fiber","muscle fiber","cardiac myofiber"],
  "A cardiac muscle cell — branched and striated, joined to neighbors by intercalated discs.",None),
 # ===== Station 10: cardiac_histo (slide 45) =====
 ("cardiac_histo",63,49,"Nucleus (central)",["nucleus","central nucleus","nuclei"],
  "Cardiac muscle cells are usually uninucleate, with a single centrally placed nucleus.",None),
 ("cardiac_histo",22,52,"Striations",["striations","cross striations","striation","cross-striations"],
  "Regular banding of overlapping actin and myosin filaments — cardiac muscle is striated.",None),
 ("cardiac_histo",43,64,"Myofiber",["myofiber","cardiac muscle cell","muscle fiber","cardiac muscle fiber","muscle fibre"],
  "A cardiac muscle cell — short, branched, and striated, joined end-to-end by intercalated discs.",None),
 # ===== Station 11: heart_wall (pericardium & wall layers) =====
 ("heart_wall",33,52,"Endocardium",["endocardium"],
  "Smooth inner endothelial lining of the heart chambers and valves.",None),
 ("heart_wall",43,62,"Myocardium",["myocardium"],
  "Thick middle layer of cardiac muscle that contracts to pump blood.",None),
 ("heart_wall",58,74,"Epicardium (visceral serous pericardium)",["epicardium","visceral pericardium","visceral serous pericardium","visceral layer of serous pericardium"],
  "Outermost layer of the heart wall — the visceral layer of the serous pericardium.",None),
 ("heart_wall",60,54,"Pericardial cavity",["pericardial cavity"],
  "Fluid-filled space between the visceral and parietal serous layers that lets the heart beat with little friction.",None),
 ("heart_wall",63,66,"Parietal layer of serous pericardium",["parietal pericardium","parietal serous pericardium","parietal layer of serous pericardium","serous pericardium","serous layer"],
  "Serous membrane lining the fibrous pericardium; forms the outer wall of the pericardial cavity.",None),
 ("heart_wall",67,58,"Fibrous pericardium",["fibrous pericardium","fibrous layer","fibrous layer of pericardium"],
  "Tough outer connective-tissue sac that anchors the heart and keeps it from overfilling.",None),
 # ===== Station 12: resp_overview =====
 ("resp_overview",33,23,"Nasal cavity",["nasal cavity","nose","nasal"],
  "Warms, humidifies, and filters incoming air before it travels to the lungs.",None),
 ("resp_overview",43,32,"Pharynx",["pharynx","throat"],
  "Shared passageway that conducts air (and, in its lower parts, food) toward the larynx and esophagus.",None),
 ("resp_overview",41,42,"Larynx",["larynx","voice box"],
  "Voice box; routes air into the trachea, produces sound, and keeps food out of the airway.",None),
 ("resp_overview",46,46,"Trachea",["trachea","windpipe"],
  "Windpipe; conducts air between the larynx and the bronchi.",None),
 ("resp_overview",46,59,"Main (primary) bronchus",["main bronchus","primary bronchus","bronchus","main bronchi","primary bronchi"],
  "Conducts air from the trachea into a lung.",None),
 ("resp_overview",35,66,"Lung",["lung","lungs"],
  "Organ of gas exchange where oxygen enters the blood and carbon dioxide leaves it.",None),
 ("resp_overview",45,80,"Diaphragm",["diaphragm"],
  "Main muscle of inspiration; contracts and flattens to draw air into the lungs.",None),
 # ===== Station 11: resp_upper (nasal & pharynx) =====
 ("resp_upper",52,20,"Nasal conchae",["nasal conchae","conchae","concha","turbinates","nasal concha"],
  "Scroll-like projections that warm, humidify, and filter air by increasing the nasal surface area.",None),
 ("resp_upper",45,17,"Nasal meatus",["nasal meatus","meatus","meatuses","meati"],
  "Air passages beneath each concha that channel airflow through the nasal cavity.",None),
 ("resp_upper",56,29,"Nasal vestibule",["nasal vestibule","vestibule"],
  "Entrance to the nasal cavity, just inside the nostril.",None),
 ("resp_upper",59,31,"External nares (nostril)",["external nares","nares","nostril","nostrils","naris","anterior nares"],
  "The nostrils — the openings where air enters the nasal cavity.",None),
 ("resp_upper",53,33,"Hard palate",["hard palate"],
  "Bony front of the roof of the mouth that separates the oral and nasal cavities.",None),
 ("resp_upper",50,37,"Soft palate",["soft palate"],
  "Muscular back of the palate; rises to block the nasopharynx during swallowing.",None),
 ("resp_upper",43,41,"Uvula",["uvula"],
  "Fleshy tip of the soft palate that helps close off the nasopharynx during swallowing.",None),
 ("resp_upper",37,26,"Opening of auditory (pharyngotympanic) tube",["opening of auditory tube","auditory tube","pharyngotympanic tube","eustachian tube","auditory tube opening"],
  "Opening that equalizes air pressure between the middle ear and the nasopharynx.",None),
 ("resp_upper",35,30,"Nasopharynx",["nasopharynx"],
  "Uppermost part of the pharynx behind the nasal cavity; an air-only passage.",None),
 ("resp_upper",38,46,"Oropharynx",["oropharynx"],
  "Middle part of the pharynx behind the mouth; a shared passage for air and food.",None),
 ("resp_upper",40,53,"Laryngopharynx",["laryngopharynx","hypopharynx"],
  "Lowest part of the pharynx; a shared passage opening into the larynx and esophagus.",None),
 ("resp_upper",45,50,"Epiglottis",["epiglottis"],
  "Flap of cartilage that covers the laryngeal opening during swallowing to keep food out of the airway.",None),
 ("resp_upper",43,62,"Vocal fold (vocal cords)",["vocal fold","vocal folds","vocal cords","vocal cord","true vocal cords"],
  "Folds in the larynx that vibrate as air passes to produce sound.",None),
 ("resp_upper",40,63,"Glottis",["glottis","rima glottidis"],
  "The vocal folds together with the opening between them (rima glottidis) through which air passes to make sound.",None),
 ("resp_upper",46,60,"Thyroid cartilage",["thyroid cartilage"],
  "Largest laryngeal cartilage; forms the 'Adam's apple' and protects the vocal cords.",None),
 ("resp_upper",45,66,"Cricoid cartilage",["cricoid cartilage","cricoid"],
  "Ring-shaped cartilage that supports the larynx and connects it to the trachea.",None),
 ("resp_upper",42,86,"Trachea",["trachea","windpipe"],
  "Windpipe; conducts air between the larynx and the bronchi.",None),
 # ===== Station 12: resp_larynx =====
 ("resp_larynx",43,4,"Epiglottis",["epiglottis"],
  "Flap of cartilage that folds over the airway during swallowing to keep food out of the larynx.",None),
 ("resp_larynx",41,14,"Thyroid cartilage",["thyroid cartilage"],
  "Largest laryngeal cartilage ('Adam's apple'); protects the vocal cords.",None),
 ("resp_larynx",41,26,"Cricothyroid ligament",["cricothyroid ligament","cricothyroid membrane"],
  "Connects the thyroid cartilage to the cricoid cartilage below it.",None),
 ("resp_larynx",44,30,"Cricoid cartilage",["cricoid cartilage","cricoid"],
  "Ring-shaped cartilage at the base of the larynx that connects it to the trachea.",None),
 ("resp_larynx",45,34,"Tracheal cartilages",["tracheal cartilages","tracheal cartilage","tracheal rings","c-rings","c rings"],
  "C-shaped rings of cartilage that hold the trachea open.",None),
 # ===== Station 13: resp_lungs =====
 ("resp_lungs",45,8,"Trachea",["trachea","windpipe"],
  "Windpipe; conducts air toward the lungs and divides at the carina.",None),
 ("resp_lungs",48,30,"Carina",["carina"],
  "Ridge where the trachea splits into the two main bronchi; a sensitive cough trigger.",None),
 ("resp_lungs",53,33,"Main (primary) bronchus",["main bronchus","primary bronchus","bronchus","main bronchi","primary bronchi"],
  "Conducts air from the trachea into a lung.",None),
 ("resp_lungs",61,42,"Lobar (secondary) bronchus",["lobar bronchus","secondary bronchus","lobar bronchi","secondary bronchi"],
  "Branch of the main bronchus that supplies one lobe of a lung.",None),
 ("resp_lungs",64,56,"Segmental (tertiary) bronchus",["segmental bronchus","tertiary bronchus","segmental bronchi","tertiary bronchi"],
  "Branch of a lobar bronchus that supplies one bronchopulmonary segment.",None),
 ("resp_lungs",27,37,"Right superior lobe",["right superior lobe","superior lobe","right upper lobe","upper lobe"],
  "Upper lobe of the right lung — the right lung has three lobes.",None),
 ("resp_lungs",27,68,"Right middle lobe",["right middle lobe","middle lobe"],
  "Middle lobe of the right lung; found only on the right side.",None),
 ("resp_lungs",28,80,"Right inferior lobe",["right inferior lobe","inferior lobe","right lower lobe","lower lobe"],
  "Lower lobe of the right lung.",None),
 ("resp_lungs",60,17,"Left superior lobe",["left superior lobe","left upper lobe"],
  "Upper lobe of the left lung — the left lung has two lobes.",None),
 ("resp_lungs",66,81,"Left inferior lobe",["left inferior lobe","left lower lobe"],
  "Lower lobe of the left lung.",None),
 # ===== Station 14: resp_alveoli =====
 ("resp_alveoli",50,47,"Respiratory bronchiole",["respiratory bronchiole","bronchiole"],
  "Smallest airway; leads air to the alveolar ducts and has a few alveoli of its own.",None),
 ("resp_alveoli",47,28,"Alveolar duct / sac",["alveolar duct","alveolar sac","alveolar sac/duct","alveolar ducts","alveolar sacs"],
  "Passage that channels air from the bronchiole into clusters of alveoli.",None),
 ("resp_alveoli",82,49,"Alveolus",["alveolus","alveoli","alveolar"],
  "Tiny air sac where gas exchange occurs between the air and the blood.",None),
 ("resp_alveoli",54,56,"Pulmonary arteriole",["pulmonary arteriole","arteriole"],
  "Small vessel that delivers deoxygenated blood to the alveolar capillaries.",None),
 ("resp_alveoli",49,65,"Pulmonary venule",["pulmonary venule","venule"],
  "Small vessel that carries freshly oxygenated blood away from the alveoli.",None),
 # ===== Station 15: resp_trachea_histo (slide 9) =====
 ("resp_trachea_histo",55,42,"Pseudostratified ciliated columnar epithelium",["pseudostratified ciliated columnar epithelium","pseudostratified columnar epithelium","pseudostratified epithelium","respiratory epithelium"],
  "Lining of the trachea that traps inhaled debris in mucus and sweeps it upward.",None),
 ("resp_trachea_histo",38,44,"Cilia",["cilia","cilium"],
  "Hair-like projections that sweep mucus and trapped particles up toward the throat.",None),
 ("resp_trachea_histo",16,32,"Goblet cell",["goblet cell","goblet cells","goblet"],
  "Secretes the mucus that traps inhaled dust and microbes.",None),
 ("resp_trachea_histo",26,56,"Mucosa",["mucosa","tracheal mucosa"],
  "Inner lining of the trachea — the epithelium plus the underlying lamina propria (loose connective tissue).",None),
 ("resp_trachea_histo",72,71,"Tracheal (seromucous) glands",["tracheal glands","seromucous glands","submucosal glands","tracheal gland","seromucous gland"],
  "Glands in the submucosa that secrete watery mucus onto the tracheal lining.",None),
 # ===== Station 16: resp_pleura (membranes) =====
 ("resp_pleura",90,32,"Parietal pleura",["parietal pleura"],
  "Serous membrane lining the chest wall — the outer pleural layer.",None),
 ("resp_pleura",88,38,"Pleural cavity",["pleural cavity","pleural space"],
  "Fluid-filled space between the two pleurae that reduces friction during breathing.",None),
 ("resp_pleura",87,45,"Visceral pleura",["visceral pleura"],
  "Serous membrane covering the surface of the lung — the inner pleural layer.",None),
 # ===== Station 17: resp_muscles =====
 ("resp_muscles",20,32,"Intercostal muscles",["intercostal muscles","intercostals","intercostal muscle","external intercostals","internal intercostals"],
  "Muscles between the ribs that raise and lower the rib cage during breathing.",None),
 ("resp_muscles",33,74,"Diaphragm",["diaphragm"],
  "Main muscle of inspiration; contracts and flattens to draw air into the lungs.",None),
]

STATIONS = {
 "heart_internal": "Station 1 · Heart — Chambers & Internal Anatomy",
 "heart_surface_ant": "Station 2 · Heart — Surface & Great Vessels (anterior)",
 "heart_surface_post": "Station 3 · Heart — Surface & Great Vessels (posterior)",
 "heart_valves": "Station 4 · Heart Valves",
 "heart_conduction": "Station 5 · Cardiac Conduction System",
 "blood_formed": "Station 6 · Blood — Formed Elements",
 "vessel_cutaway": "Station 7 · Blood Vessel — Wall Layers",
 "vessel_cross": "Station 8 · Blood Vessel — Cross-Section",
 "cardiac_dia": "Station 9 · Cardiac Muscle — Intercalated Discs",
 "cardiac_histo": "Station 10 · Cardiac Muscle — Histology (Slide 45)",
 "heart_wall": "Station 11 · Heart Wall & Pericardium",
 "resp_overview": "Station 12 · Respiratory System Overview",
 "resp_upper": "Station 13 · Upper Airway — Nasal Cavity & Pharynx",
 "resp_larynx": "Station 14 · Larynx",
 "resp_lungs": "Station 15 · Lungs — Lobes & Bronchial Tree",
 "resp_alveoli": "Station 16 · Alveoli — Lung Histology",
 "resp_trachea_histo": "Station 17 · Trachea — Histology",
 "resp_pleura": "Station 18 · Pleural Membranes",
 "resp_muscles": "Station 19 · Respiratory Muscles",
}

# ---- image credits (shown in the start-screen "Image credits" panel) ----
# Grouped by source. Only what is actually verifiable is asserted; unconfirmed
# provenance is labelled as such rather than invented.
CREDITS = [
    {"what": "Respiratory diagrams — system overview, upper airway, larynx, "
             "lungs & bronchial tree, trachea histology, and pleurae",
     "src": "OpenStax, <em>Anatomy and Physiology</em>",
     "lic": "CC BY 4.0",
     "url": "https://openstax.org/details/books/anatomy-and-physiology"},
    {"what": "Heart wall &amp; pericardium diagram",
     "src": "OpenStax College, <em>Anatomy &amp; Physiology</em> (via Wikimedia Commons, &ldquo;2004 Heart Wall&rdquo;)",
     "lic": "CC BY 3.0",
     "url": "https://commons.wikimedia.org/wiki/File:2004_Heart_Wall.jpg"},
    {"what": "Cardiac muscle histology micrograph (slide&nbsp;45)",
     "src": "RWhitwam, Wikimedia Commons (&ldquo;Cardiac muscle 305&rdquo;, labels cropped)",
     "lic": "CC BY-SA 4.0",
     "url": "https://commons.wikimedia.org/wiki/File:Cardiac_muscle_305.png"},
    {"what": "Alveolus / lung-histology diagram",
     "src": "Wikimedia Commons (original labels cropped) — specific file &amp; author to be confirmed",
     "lic": "likely CC BY-SA",
     "url": ""},
    {"what": "Histology micrographs — blood formed elements (slide&nbsp;16), "
             "artery/vein/nerve wall (slide&nbsp;3), cardiac muscle (slide&nbsp;45)",
     "src": "BIOL&nbsp;40B lab slide collection",
     "lic": "course materials",
     "url": ""},
    {"what": "Heart illustrations — internal section, external surface, valves, conduction system",
     "src": "Source not individually recorded — confirm (or swap for a known-free equivalent) before public distribution",
     "lic": "",
     "url": ""},
]

def data_uri(path, max_w=1000, quality=82):
    """Downscale to max_w and JPEG-encode (flattened on white) to keep the page lean."""
    import io
    from PIL import Image
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=quality, optimize=True)
    b = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/jpeg;base64,{b}"

from PIL import Image
assets = {}
images_payload = {}
for name, meta in IMAGES.items():
    f = meta["file"]
    if f not in assets:
        assets[f] = data_uri(IMG / f)
    w, h = Image.open(IMG / f).size
    images_payload[name] = {
        "asset": f,
        "caption": meta["caption"],
        "crop": meta["crop"],
        "covers": meta["covers"],
        "w": w, "h": h,
        "station": STATIONS[name],
    }

questions_payload = []
for img,x,y,name,answers,func,blood in Q:
    # The displayed/canonical name must always count as a correct typed answer
    # (some names have parentheticals or slashes that aren't in `answers`).
    ans = list(dict.fromkeys([*answers, name]))
    questions_payload.append({
        "img": img, "x": x, "y": y, "name": name,
        "answers": ans, "func": func, "blood": blood,
    })

payload = {"assets": assets, "images": images_payload, "questions": questions_payload,
           "order": list(IMAGES.keys()), "credits": CREDITS}

template = (BASE / "app_template.html").read_text()
html = template.replace("/*__PAYLOAD__*/null", json.dumps(payload))
OUT.write_text(html)
(BASE / "index.html").write_text(html)  # deployable copy for GitHub Pages
kb = len(html.encode())/1024
print(f"wrote {OUT} + index.html  ({kb:.0f} KB, {len(questions_payload)} questions)")
