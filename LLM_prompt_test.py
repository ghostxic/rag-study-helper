from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import time

load_dotenv()

TEST_CASES = [
    {
        "name": "Complete Information Available",
        "question": "What is the process of photosynthesis and what are its main products?",
        "context": [
            "Photosynthesis is the process by which plants convert light energy into chemical energy. During photosynthesis, plants use sunlight, water (H2O), and carbon dioxide (CO2) to produce glucose (C6H12O6) and oxygen (O2). This process occurs primarily in the chloroplasts of plant cells, specifically in structures called thylakoids. The overall equation for photosynthesis is: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2."
        ]
    },
    {
        "name": "Partial Information Available",
        "question": "Explain the causes, timeline, and consequences of the French Revolution.",
        "context": [
            "The French Revolution began in 1789 with the storming of the Bastille on July 14th. Major causes included financial crisis, food shortages, and widespread inequality. King Louis XVI was executed in 1793. The revolution led to the rise of Napoleon Bonaparte, who eventually became Emperor of France."
        ]
    },
    {
        "name": "No Relevant Information",
        "question": "What are the key differences between Python and JavaScript programming languages?",
        "context": [
            "The mitochondria is known as the powerhouse of the cell. It produces ATP through cellular respiration. Mitochondria have their own DNA and are thought to have originated from ancient bacteria through endosymbiosis. They have a double membrane structure with cristae that increase surface area for energy production."
        ]
    },
    {
        "name": "Contradictory Information",
        "question": "When did the company release its flagship product?",
        "context": [
            "According to the Q1 2023 earnings report, TechCorp released its flagship product, the X-500, in March 2023.",
            "The company's press release from February 2023 stated that the X-500 would launch in April 2023 after beta testing was completed.",
            "An interview with the CEO published in May 2023 mentioned that the X-500 had been available to customers since February 2023."
        ]
    },
    {
        "name": "Ambiguous Information",
        "question": "What is the company's policy on remote work?",
        "context": [
            "Employees may work from home when appropriate. Managers have discretion to approve flexible work arrangements based on role requirements and team needs. The company values both collaboration and work-life balance."
        ]
    },
    {
        "name": "Requires Inference (Testing Boundaries)",
        "question": "Is climate change affecting polar bear populations?",
        "context": [
            "Studies from 2020-2023 show that Arctic sea ice has declined by 13% per decade. Polar bears depend on sea ice platforms for hunting seals, their primary food source. Research conducted in Hudson Bay shows that polar bears are spending more time on land and have reduced body mass compared to measurements from the 1980s."
        ]
    },
    {
        "name": "Multiple Sources Synthesis",
        "question": "What are the recommended treatments for Type 2 diabetes?",
        "context": [
            "The American Diabetes Association guidelines recommend metformin as the first-line medication for Type 2 diabetes. Patients should also engage in at least 150 minutes of moderate-intensity aerobic activity per week.",
            "A 2022 clinical study published in the Journal of Endocrinology found that dietary modifications, including reduced sugar intake and increased fiber consumption, significantly improved blood glucose control in Type 2 diabetes patients.",
            "The Mayo Clinic reports that regular blood glucose monitoring is essential for managing Type 2 diabetes. Patients should check their levels as recommended by their healthcare provider."
        ]
    },
    {
        "name": "Technical/Complex Information",
        "question": "How does the TCP three-way handshake work?",
        "context": [
            "The TCP three-way handshake is a method used to establish a connection between a client and server. Step 1: The client sends a SYN (synchronize) packet to the server, indicating it wants to establish a connection and includes an initial sequence number. Step 2: The server responds with a SYN-ACK (synchronize-acknowledge) packet, acknowledging the client's SYN and sending its own sequence number. Step 3: The client sends an ACK (acknowledge) packet back to the server, confirming receipt of the server's SYN-ACK. After these three steps, the connection is established and data transmission can begin."
        ]
    },
    {
        "name": "Incomplete Data with Numbers",
        "question": "What were the quarterly revenue figures for all four quarters of 2023?",
        "context": [
            "The company reported strong performance in 2023. Q1 revenue was $45.2 million, representing 15% growth year-over-year. Q2 saw revenues of $48.7 million. The second half of the year showed continued momentum with Q4 reaching $55.1 million, the highest quarterly revenue in company history."
        ]
    },
    {
        "name": "Definitional Question with Precise Answer",
        "question": "What is the boiling point of water at sea level?",
        "context": [
            "Water has several important physical properties. At standard atmospheric pressure (sea level), water boils at 100 degrees Celsius or 212 degrees Fahrenheit. The boiling point decreases at higher altitudes due to lower atmospheric pressure. Water freezes at 0 degrees Celsius (32 degrees Fahrenheit) under standard conditions."
        ]
    },
    {
        "name": "Large Context - History with Mixed Relevance",
        "question": "What were the main provisions of the Treaty of Versailles?",
        "context": [
            "The Treaty of Versailles was signed on June 28, 1919, at the Palace of Versailles in France. The treaty officially ended World War I between Germany and the Allied Powers. Key provisions included: Article 231, known as the 'War Guilt Clause,' which placed full responsibility for the war on Germany and its allies. Germany was required to pay reparations totaling 132 billion gold marks (approximately $33 billion USD at the time). The treaty required Germany to disarm substantially, limiting its army to 100,000 troops, prohibiting conscription, and banning tanks, aircraft, and submarines. Germany lost significant territory, including Alsace-Lorraine to France, and all colonial possessions. The Rhineland was to be demilitarized and occupied by Allied forces for 15 years.",
            "The Palace of Versailles is a former royal residence located in Versailles, about 12 miles west of Paris, France. It was the principal residence of the Kings of France from Louis XIV in 1682 until the royal family was forced to return to Paris in October 1789. The palace is famous for its Hall of Mirrors, where many important ceremonies took place. Today, it is a popular tourist destination and a UNESCO World Heritage site, attracting millions of visitors annually.",
            "World War I, also known as the Great War, lasted from 1914 to 1918. It involved most of the world's great powers, assembled in two opposing alliances: the Allies and the Central Powers. The immediate trigger was the assassination of Archduke Franz Ferdinand of Austria on June 28, 1914. The war was characterized by trench warfare, particularly on the Western Front, and resulted in unprecedented casualties, with an estimated 16 million deaths.",
            "The League of Nations was established as part of the Treaty of Versailles. It was an international organization founded on January 10, 1920, with the goal of maintaining world peace and preventing future wars through collective security and disarmament. However, the United States Senate refused to ratify the treaty, and the U.S. never joined the League. The League ultimately failed to prevent World War II and was dissolved in 1946, replaced by the United Nations."
        ]
    },
    {
        "name": "Large Context - Science with Irrelevant Sources",
        "question": "Explain the structure and function of DNA.",
        "context": [
            "Deoxyribonucleic acid (DNA) is a molecule composed of two polynucleotide chains that coil around each other to form a double helix. The structure was first described by James Watson and Francis Crick in 1953, based on X-ray crystallography work by Rosalind Franklin. DNA is composed of four nucleotide bases: adenine (A), thymine (T), guanine (G), and cytosine (C). These bases pair specifically: A with T, and G with C, connected by hydrogen bonds. The sugar-phosphate backbone forms the outer structure of the helix. DNA's primary function is to store genetic information that provides instructions for building proteins and other molecules essential for life. Genes are specific segments of DNA that encode for particular proteins.",
            "The human digestive system is a complex series of organs and glands that processes food. It includes the mouth, esophagus, stomach, small intestine, large intestine, rectum, and anus. The digestive process begins in the mouth with mechanical breakdown through chewing and chemical breakdown via salivary enzymes. The stomach continues this process with gastric acid and enzymes. Most nutrient absorption occurs in the small intestine, which has a surface area of approximately 250 square meters due to villi and microvilli.",
            "Protein synthesis is the process by which cells build proteins. It occurs in two main stages: transcription and translation. During transcription, DNA is used as a template to create messenger RNA (mRNA) in the nucleus. The mRNA then travels to ribosomes in the cytoplasm, where translation occurs. Transfer RNA (tRNA) molecules bring specific amino acids to the ribosome based on the mRNA sequence, and these amino acids are linked together to form a protein chain.",
            "The Grand Canyon is a steep-sided canyon carved by the Colorado River in Arizona. It is 277 miles long, up to 18 miles wide, and attains a depth of over a mile. The canyon reveals approximately two billion years of Earth's geological history through its exposed rock layers. It was designated a UNESCO World Heritage Site in 1979 and attracts approximately 6 million visitors per year."
        ]
    },
    {
        "name": "Mixed Relevance - Business Question",
        "question": "What factors contributed to the company's Q3 2023 revenue decline?",
        "context": [
            "In Q3 2023, the company experienced a 12% revenue decline compared to Q2 2023, dropping from $85 million to $74.8 million. The CEO attributed this decline to three primary factors: increased competition in the Asian markets, supply chain disruptions affecting product availability, and delayed product launches due to regulatory approval processes in Europe.",
            "The company was founded in 1998 by Sarah Chen and Michael Rodriguez in a small garage in Palo Alto, California. Initially focused on consumer electronics, the company pivoted to enterprise software solutions in 2005. The company went public in 2015 with an initial public offering price of $18 per share.",
            "Customer satisfaction scores remained high in Q3 2023, with an average rating of 4.6 out of 5 stars. The customer service team resolved 94% of inquiries within 24 hours, exceeding the industry benchmark of 85%.",
            "In September 2023, the company announced a new partnership with DataTech Solutions to integrate artificial intelligence capabilities into its core product line. This partnership is expected to generate additional revenue streams beginning in Q1 2024."
        ]
    },
    {
        "name": "Large Technical Context - Some Relevant",
        "question": "What are the key differences between supervised and unsupervised machine learning?",
        "context": [
            "Machine learning is a subset of artificial intelligence that focuses on developing algorithms that can learn from and make predictions or decisions based on data. There are three main categories of machine learning: supervised learning, unsupervised learning, and reinforcement learning.",
            "Supervised learning uses labeled training data to learn the relationship between inputs and outputs. In supervised learning, each training example consists of an input and its corresponding correct output (label). The algorithm learns to map inputs to outputs by minimizing prediction errors. Common supervised learning tasks include classification (predicting categories) and regression (predicting continuous values). Examples of supervised learning algorithms include linear regression, logistic regression, decision trees, random forests, support vector machines, and neural networks. Supervised learning requires a large amount of labeled data, which can be time-consuming and expensive to obtain.",
            "Quantum computing is an emerging technology that uses quantum mechanical phenomena such as superposition and entanglement to perform computations. Unlike classical computers that use bits (0 or 1), quantum computers use quantum bits or qubits, which can exist in multiple states simultaneously. This allows quantum computers to solve certain problems exponentially faster than classical computers. Major tech companies like IBM, Google, and Microsoft are investing heavily in quantum computing research.",
            "Unsupervised learning works with unlabeled data and tries to find hidden patterns or structures within the data without explicit guidance. The algorithm explores the data and draws inferences without being told what to look for. Common unsupervised learning tasks include clustering (grouping similar data points together), dimensionality reduction (reducing the number of features while preserving important information), and anomaly detection (identifying unusual patterns). Examples of unsupervised learning algorithms include K-means clustering, hierarchical clustering, principal component analysis (PCA), and autoencoders. Unsupervised learning is useful when labeled data is unavailable or when you want to discover previously unknown patterns in data.",
            "Cloud computing refers to the delivery of computing services—including servers, storage, databases, networking, software, analytics, and intelligence—over the Internet ('the cloud') to offer faster innovation, flexible resources, and economies of scale. Major cloud service providers include Amazon Web Services (AWS), Microsoft Azure, and Google Cloud Platform. Cloud computing has three main service models: Infrastructure as a Service (IaaS), Platform as a Service (PaaS), and Software as a Service (SaaS)."
        ]
    },
    {
        "name": "Multiple Long Sources - Medical Context",
        "question": "What are the stages and symptoms of Alzheimer's disease?",
        "context": [
            "Alzheimer's disease is a progressive neurological disorder that causes brain cells to degenerate and die, leading to a continuous decline in thinking, behavioral, and social skills. It is the most common cause of dementia, accounting for 60-80% of dementia cases. The disease typically progresses through several stages. In the preclinical stage, changes occur in the brain years before symptoms appear, though the person functions normally. During mild cognitive impairment (MCI), there are noticeable changes in memory and thinking, but the person can still perform daily activities independently. In mild Alzheimer's disease (early-stage), symptoms include memory loss, difficulty with problem-solving, changes in personality, getting lost, and difficulty managing finances. The person may still be able to function independently in some areas.",
            "Moderate Alzheimer's disease (middle-stage) is typically the longest stage and can last for many years. Symptoms become more pronounced and include: increased memory loss and confusion, difficulty recognizing family and friends, inability to learn new things, difficulty with language and problems with reading and writing, inability to organize thoughts or think logically, shortened attention span, problems coping with new situations, difficulty with multi-step tasks like getting dressed, impulsive behavior, and hallucinations, delusions, and paranoia. Individuals at this stage require more assistance with daily activities.",
            "Severe Alzheimer's disease (late-stage) is the final stage where individuals lose the ability to respond to their environment, carry on a conversation, and eventually control movement. Symptoms include: inability to communicate coherently, need for full-time assistance with personal care, significant personality changes, loss of awareness of recent experiences and surroundings, physical changes including difficulty swallowing, weight loss, seizures, skin infections, increased sleeping, and loss of bowel and bladder control. In the final stages, individuals are typically bed-bound. The average life expectancy after diagnosis is 4-8 years, though some people may live as long as 20 years with the disease.",
            "The cardiovascular system, also called the circulatory system, is the organ system that allows blood to circulate and transport nutrients, oxygen, carbon dioxide, hormones, and blood cells throughout the body. The heart is a muscular organ that pumps blood through blood vessels. The average adult heart beats about 100,000 times per day, pumping approximately 2,000 gallons of blood. Regular exercise, a healthy diet, and avoiding smoking are important for maintaining cardiovascular health.",
            "Risk factors for Alzheimer's disease include advancing age (most common in people over 65), family history and genetics (having a first-degree relative with Alzheimer's increases risk), the APOE-e4 gene variant, Down syndrome, mild cognitive impairment, past head trauma, poor sleep patterns, lifestyle factors (lack of exercise, obesity, smoking, high blood pressure, high cholesterol, poorly controlled diabetes), and lower levels of education and social engagement. While these factors increase risk, they don't guarantee someone will develop the disease."
        ]
    },
    {
        "name": "Historical Event - Mixed Relevance Sources",
        "question": "What were the causes and consequences of the Industrial Revolution?",
        "context": [
            "The Agricultural Revolution of the 18th century in Britain preceded and enabled the Industrial Revolution. New farming techniques, including crop rotation, selective breeding of livestock, and the enclosure movement, increased agricultural productivity. This led to a surplus of food, population growth, and the displacement of rural workers who moved to cities seeking employment. The availability of capital from agricultural profits and colonial trade also provided funding for industrial ventures.",
            "The Industrial Revolution began in Britain in the late 18th century and spread to other parts of Europe and North America in the 19th century. Key causes included: the availability of natural resources (especially coal and iron ore), technological innovations (the steam engine, spinning jenny, power loom), transportation improvements (canals and railways), a stable political system and strong property rights that encouraged investment, access to colonial markets and raw materials, and a growing population providing both labor and consumers.",
            "The Renaissance was a period of cultural, artistic, political, and economic rebirth following the Middle Ages. It began in Italy in the 14th century and spread throughout Europe. Key figures included Leonardo da Vinci, Michelangelo, and Raphael in art, and Dante, Petrarch, and Machiavelli in literature. The Renaissance emphasized humanism, individualism, and the rediscovery of classical Greek and Roman texts.",
            "The consequences of the Industrial Revolution were profound and far-reaching. Economically, it led to unprecedented growth in production and wealth, the emergence of capitalism and factory systems, and the rise of new social classes (industrial capitalists and the urban working class). Socially, it caused rapid urbanization, poor living and working conditions in early factories and cities, child labor, and eventually labor movements and reforms. Technologically, it drove continuous innovation in manufacturing, transportation, and communication. Environmentally, it initiated large-scale pollution and resource exploitation. Politically, it shifted power from landowners to industrial capitalists and eventually led to political reforms expanding suffrage."
        ]
    },
    {
        "name": "Literature Analysis - Partially Relevant",
        "question": "What are the main themes in George Orwell's '1984'?",
        "context": [
            "George Orwell's '1984,' published in 1949, explores several interconnected themes. Totalitarianism is the central theme, depicting a society under complete government control. The novel shows how the Party maintains power through surveillance (telescreens), propaganda (Ministry of Truth), thought control (Thoughtcrime and Newspeak), and perpetual war. The theme of psychological manipulation is evident in the Party's ability to control reality itself, as expressed in the slogan 'Who controls the past controls the future. Who controls the present controls the past.' The destruction of language through Newspeak demonstrates how limiting vocabulary limits thought itself.",
            "George Orwell, born Eric Arthur Blair in 1903, was a British novelist, essayist, and journalist. He fought in the Spanish Civil War, which influenced his opposition to totalitarianism. Other notable works include 'Animal Farm' (1945) and essays like 'Politics and the English Language' (1946). He died of tuberculosis in 1950 at age 46.",
            "The themes of love and loyalty are explored through Winston's relationship with Julia. Their affair is an act of rebellion, though ultimately the Party destroys their bond. The novel questions whether authentic human connection is possible under totalitarianism. The theme of individuality versus collective identity is central—Winston's struggle to maintain his individual thoughts and memories against the Party's attempts to subsume all identity into collective obedience. The manipulation of truth and objective reality is another major theme, encapsulated in the concept of 'doublethink'—simultaneously holding two contradictory beliefs.",
            "Aldous Huxley's 'Brave New World,' published in 1932, is another famous dystopian novel. It depicts a future world where people are genetically engineered and conditioned to be happy with their predetermined roles in society. The World State uses pleasure, drugs (soma), and entertainment to control the population, contrasting with Orwell's vision of control through fear and pain."
        ]
    },
    {
        "name": "Economics - Multiple Long Documents",
        "question": "Explain the concept of supply and demand and how it determines market prices.",
        "context": [
            "Supply and demand is a fundamental economic model that explains how prices are determined in a market economy. The law of demand states that, all else being equal, as the price of a good increases, the quantity demanded decreases, and vice versa. This inverse relationship exists because consumers have limited budgets and seek to maximize utility. At higher prices, fewer consumers are willing or able to purchase the good. At lower prices, more consumers find the good affordable and desirable. The demand curve typically slopes downward from left to right on a graph plotting price versus quantity.",
            "The law of supply states that, all else being equal, as the price of a good increases, the quantity supplied increases, and vice versa. This direct relationship exists because higher prices provide greater incentive for producers to manufacture and sell goods, as they can earn more profit. At higher prices, existing suppliers produce more, and new suppliers may enter the market. The supply curve typically slopes upward from left to right. Factors affecting supply include production costs, technology, number of sellers, expectations about future prices, and prices of related goods in production.",
            "Market equilibrium occurs at the price point where the quantity demanded equals the quantity supplied. This is where the supply and demand curves intersect. At the equilibrium price, there is no shortage or surplus—the market clears. If the current price is above equilibrium, there is a surplus (excess supply), and sellers will lower prices to sell their inventory. If the current price is below equilibrium, there is a shortage (excess demand), and competition among buyers drives prices up. Through this mechanism, markets naturally tend toward equilibrium.",
            "Keynesian economics, developed by John Maynard Keynes during the Great Depression, argues that government intervention is necessary to stabilize the economy. Keynes believed that aggregate demand (total spending in the economy) drives economic output and employment in the short run. During recessions, governments should increase spending and cut taxes to stimulate demand. This contrasts with classical economics, which emphasizes the self-correcting nature of markets and limited government intervention.",
            "Changes in market conditions cause shifts in supply or demand curves, leading to new equilibrium prices. Demand curve shifts occur due to changes in consumer income, preferences, prices of substitute or complementary goods, consumer expectations, or number of buyers. An increase in demand (rightward shift) leads to higher equilibrium price and quantity. Supply curve shifts occur due to changes in production costs, technology, prices of inputs, producer expectations, number of sellers, or government policies like taxes or subsidies. An increase in supply (rightward shift) leads to lower equilibrium price and higher equilibrium quantity."
        ]
    },
    {
        "name": "Environmental Science - Mixed Sources",
        "question": "What is ocean acidification and what causes it?",
        "context": [
            "Ocean acidification refers to the ongoing decrease in the pH of the Earth's oceans, caused by the uptake of carbon dioxide (CO2) from the atmosphere. When CO2 dissolves in seawater, it forms carbonic acid (H2CO3), which then dissociates into hydrogen ions (H+) and bicarbonate ions (HCO3-). The increase in hydrogen ions causes the water to become more acidic. Since the Industrial Revolution, ocean pH has decreased by approximately 0.1 units, from 8.2 to 8.1, representing a 30% increase in acidity. This process is happening faster than at any time in the past 300 million years.",
            "The main cause of ocean acidification is the burning of fossil fuels (coal, oil, and natural gas), which releases large amounts of CO2 into the atmosphere. The ocean absorbs approximately 30% of the CO2 released by human activities. Other contributing factors include deforestation, which reduces CO2 absorption by trees, and cement production. The rate of ocean acidification is directly linked to atmospheric CO2 concentrations, which have increased from about 280 parts per million (ppm) in pre-industrial times to over 415 ppm today.",
            "Coral reefs are among the most biologically diverse ecosystems on Earth, providing habitat for approximately 25% of all marine species despite covering less than 1% of the ocean floor. They offer numerous benefits including coastal protection from storms and erosion, tourism revenue, and fisheries support. However, coral reefs are threatened by multiple stressors including rising ocean temperatures, pollution, overfishing, and coastal development.",
            "The effects of ocean acidification are particularly severe for calcifying organisms—species that build shells or skeletons from calcium carbonate. As ocean pH decreases, it becomes more difficult for organisms like corals, shellfish, pteropods (sea butterflies), and some plankton species to form and maintain their calcium carbonate structures. This is because lower pH reduces the availability of carbonate ions (CO3 2-) needed for calcification. Studies show that some shellfish larvae already struggle to develop shells in current ocean conditions. Beyond calcifying organisms, ocean acidification affects fish behavior, sensory abilities, and reproduction, and may disrupt entire marine food webs."
        ]
    },
    {
        "name": "Technology - Blockchain with Irrelevant Context",
        "question": "How does blockchain technology work?",
        "context": [
            "The history of the internet dates back to the 1960s with the development of ARPANET, a project funded by the U.S. Department of Defense. The World Wide Web was invented by Tim Berners-Lee in 1989 while working at CERN. The commercialization of the internet in the 1990s led to the dot-com boom and fundamentally transformed communication, commerce, and information access globally.",
            "Blockchain is a distributed ledger technology that maintains a continuously growing list of records called blocks. Each block contains a cryptographic hash of the previous block, a timestamp, and transaction data. The chain of blocks is distributed across a network of computers (nodes) rather than stored in a central location. Here's how it works: When a transaction occurs, it is broadcast to all nodes in the network. Nodes validate the transaction using predetermined rules. Valid transactions are collected into a new block. Miners or validators compete to add the new block to the chain, typically by solving a complex mathematical problem (in proof-of-work systems) or through other consensus mechanisms like proof-of-stake.",
            "Once a block is added to the blockchain, it is extremely difficult to alter because changing any information in a block would require recalculating the hash for that block and all subsequent blocks, and gaining approval from the majority of the network. This immutability makes blockchain secure and trustworthy without requiring a central authority. Key features include: decentralization (no single point of control or failure), transparency (all participants can view the entire transaction history), immutability (past records cannot be easily altered), and security through cryptography.",
            "Social media platforms have revolutionized how people communicate and share information. Facebook was founded in 2004, YouTube in 2005, Twitter in 2006, and Instagram in 2010. These platforms have billions of users worldwide and have significant impacts on politics, marketing, journalism, and social movements. However, they also raise concerns about privacy, misinformation, and mental health effects."
        ]
    },
    {
        "name": "Philosophy - Some Relevant Context",
        "question": "What is Plato's Theory of Forms?",
        "context": [
            "Plato's Theory of Forms, also called the Theory of Ideas, is a fundamental doctrine in his philosophy. According to this theory, the physical world we perceive through our senses is not the true reality but merely an imperfect reflection of a higher realm of perfect, eternal, and unchanging Forms or Ideas. For example, all physical circles are imperfect approximations of the perfect Form of Circle that exists in this higher realm. Forms are the ultimate reality—they are eternal, perfect, and exist independently of the physical world. Physical objects are merely shadows or copies of these Forms. Plato illustrates this with the Allegory of the Cave, where prisoners see only shadows on a wall and mistake them for reality.",
            "Aristotle was Plato's student but disagreed with the Theory of Forms. Aristotle developed his own philosophy emphasizing empirical observation and arguing that forms exist within objects themselves, not in a separate realm. He established the Lyceum in Athens and tutored Alexander the Great. Aristotle's works covered logic, ethics, politics, biology, and physics, profoundly influencing Western philosophy and science.",
            "Knowledge, for Plato, consists of understanding these eternal Forms through reason and philosophical contemplation, not through sensory experience. The soul is immortal and has knowledge of the Forms from before birth; learning is therefore recollection (anamnesis). Only philosophers who have grasped the Forms, particularly the Form of the Good, are truly wise and fit to rule society, as described in 'The Republic.'",
            "The Pre-Socratic philosophers were early Greek thinkers who preceded Socrates, including Thales, Heraclitus, Parmenides, and Democritus. They sought natural explanations for phenomena rather than mythological ones. Thales proposed that water was the fundamental substance of all things. Heraclitus emphasized constant change ('you cannot step into the same river twice'). Democritus proposed atomic theory, suggesting that everything is composed of indivisible atoms moving in void."
        ]
    },
    {
        "name": "Legal Case Analysis - Multiple Long Documents",
        "question": "What was the ruling and significance of Brown v. Board of Education?",
        "context": [
            "Brown v. Board of Education of Topeka, 347 U.S. 483 (1954), was a landmark Supreme Court case that declared state laws establishing separate public schools for black and white students unconstitutional. The case was actually a consolidation of five cases from different states. The lead case involved Linda Brown, a black third-grader in Topeka, Kansas, who had to walk a mile through a railroad switchyard to attend an all-black school, even though an all-white school was just seven blocks from her home. The NAACP Legal Defense Fund, led by Thurgood Marshall (who later became the first African American Supreme Court Justice), represented the plaintiffs.",
            "The Court's unanimous decision, delivered by Chief Justice Earl Warren, overturned the 'separate but equal' doctrine established by Plessy v. Ferguson (1896). The Court concluded that 'separate educational facilities are inherently unequal' and violate the Equal Protection Clause of the Fourteenth Amendment. Warren wrote: 'We conclude that in the field of public education the doctrine of 'separate but equal' has no place. Separate educational facilities are inherently unequal.' The decision was based partly on social science research, including studies by psychologists Kenneth and Mamie Clark showing that segregation damaged the self-esteem of black children.",
            "The Miranda v. Arizona case (1966) established the requirement that police inform suspects of their rights before custodial interrogation. This led to the famous 'Miranda rights' that must be read to arrested individuals: the right to remain silent, that anything said can be used in court, the right to an attorney, and that an attorney will be provided if they cannot afford one. The case involved Ernesto Miranda, who confessed to crimes without being informed of his constitutional rights.",
            "The significance of Brown v. Board of Education was enormous. It was a major victory for the Civil Rights Movement and served as a catalyst for further civil rights legislation and activism. However, implementation was slow and met with massive resistance, particularly in the South. Some states closed public schools rather than integrate. In 1955, the Court issued Brown II, ordering desegregation to proceed 'with all deliberate speed,' but this vague timeline allowed continued delays. Federal intervention was sometimes necessary, as in the 1957 Little Rock Crisis when President Eisenhower sent federal troops to enforce integration. The decision's impact extended beyond education, providing legal precedent for challenging segregation in other areas of public life.",
            "The legal doctrine of stare decisis means 'to stand by things decided' and refers to the principle that courts should follow precedent set by previous decisions. This promotes consistency, predictability, and stability in the legal system. However, courts can overturn precedent when there are compelling reasons, as Brown v. Board of Education did with Plessy v. Ferguson."
        ]
    },
    {
        "name": "Astronomy - Mixed Relevant/Irrelevant",
        "question": "What is a black hole and how is it formed?",
        "context": [
            "A black hole is a region of spacetime where gravity is so strong that nothing, not even light, can escape from it. The boundary of a black hole is called the event horizon—once something crosses this boundary, it cannot escape. Black holes are invisible themselves, but their presence can be detected by observing their effects on nearby matter and light. The term 'black hole' was coined by physicist John Wheeler in 1967, though the concept was predicted by Einstein's general theory of relativity.",
            "Black holes are formed when massive stars (typically more than 20 times the mass of our Sun) reach the end of their life cycle. When such a star exhausts its nuclear fuel, it can no longer support itself against its own gravity. The core collapses catastrophically in a supernova explosion. If the remaining core mass is above approximately 3 solar masses (the Tolman-Oppenheimer-Volkoff limit), the collapse continues beyond a neutron star to form a black hole. The matter is compressed into an infinitely small point called a singularity, where density becomes infinite and the laws of physics as we know them break down.",
            "The Solar System consists of the Sun and all objects gravitationally bound to it, including eight planets, their moons, dwarf planets like Pluto, asteroids, comets, and other small bodies. The planets in order from the Sun are Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune. Jupiter is the largest planet, while Mercury is the smallest. The asteroid belt lies between Mars and Jupiter. The Solar System formed approximately 4.6 billion years ago from the gravitational collapse of a region within a large molecular cloud.",
            "There are different types of black holes based on their mass. Stellar black holes, formed from collapsed stars, typically have masses between 3 and several tens of solar masses. Supermassive black holes, found at the centers of most galaxies including our Milky Way, have masses ranging from millions to billions of solar masses. How these supermassive black holes formed is still debated—they may have grown by accreting mass over billions of years or formed from the direct collapse of massive gas clouds in the early universe. Intermediate-mass black holes, with masses between stellar and supermassive black holes, have also been detected. Primordial black holes are hypothetical black holes that may have formed in the early universe."
        ]
    },
    {
        "name": "Psychology - Complex with Distractors",
        "question": "What are the main stages of cognitive development according to Piaget?",
        "context": [
            "Jean Piaget (1896-1980) was a Swiss psychologist known for his groundbreaking work in child development and cognitive theory. His theory of cognitive development proposes that children progress through four distinct stages of intellectual development, each characterized by qualitatively different ways of thinking and understanding the world.",
            "The Sensorimotor Stage (birth to approximately 2 years) is the first stage. During this period, infants learn about the world through their senses and motor actions. Key achievements include: developing object permanence (understanding that objects continue to exist even when they cannot be seen, heard, or touched), beginning to engage in goal-directed behavior, and starting to use mental representations. Infants are initially very egocentric but gradually begin to differentiate themselves from their environment.",
            "Sigmund Freud developed psychoanalytic theory, which emphasizes the role of unconscious processes and childhood experiences in shaping personality and behavior. Freud proposed that personality consists of three parts: the id (instinctive drives), the ego (rational, decision-making part), and the superego (moral conscience). He also outlined psychosexual stages of development: oral, anal, phallic, latency, and genital. Though influential, many of Freud's ideas have been criticized and revised by later psychologists.",
            "The Preoperational Stage (approximately 2 to 7 years) is characterized by the development of language and symbolic thought, but thinking is still intuitive rather than logical. Children in this stage: engage in pretend play and use symbols (like words and images) to represent objects, are egocentric (difficulty seeing perspectives other than their own), lack conservation (understanding that quantity remains the same despite changes in shape or appearance), and display animism (attributing life-like qualities to inanimate objects). For example, a child might believe that pouring water from a short, wide cup into a tall, thin glass means there's now more water.",
            "The Concrete Operational Stage (approximately 7 to 11 years) marks the beginning of logical thinking, but only about concrete, tangible objects and situations. Children develop: conservation (understanding that quantity, length, or number stays the same despite changes in shape or arrangement), classification skills (ability to group objects by common properties), seriation (ability to arrange objects in logical order, such as by size), and reversibility (understanding that actions can be reversed). However, they still struggle with abstract or hypothetical thinking.",
            "The Formal Operational Stage (approximately 11 years and older) is the final stage, where individuals develop the ability to think abstractly, reason logically about hypothetical situations, and engage in systematic problem-solving. Capabilities include: abstract thinking (reasoning about concepts not physically present), hypothetical-deductive reasoning (generating and testing hypotheses systematically), metacognition (thinking about one's own thinking), and considering multiple perspectives and possibilities. Not all individuals fully develop formal operational thinking, and cultural and educational factors influence its development.",
            "B.F. Skinner was a behaviorist psychologist who emphasized the role of reinforcement and punishment in shaping behavior. He developed operant conditioning theory, which explains how consequences affect the frequency of behaviors. Positive reinforcement (adding a pleasant stimulus) and negative reinforcement (removing an unpleasant stimulus) increase behaviors, while punishment decreases them. Skinner's work has applications in education, therapy, and animal training."
        ]
    },
    {
        "name": "Biology - Cellular Process with Irrelevant Info",
        "question": "Describe the process of mitosis and its stages.",
        "context": [
            "Mitosis is a type of cell division that results in two daughter cells, each having the same number and kind of chromosomes as the parent nucleus. It is the process by which the body produces new cells for growth and repair. Mitosis is divided into several distinct phases, which follow interphase (the period when the cell grows and replicates its DNA).",
            "The first stage is Prophase, where several key events occur: chromatin condenses into visible chromosomes, each consisting of two sister chromatids joined at the centromere; the nuclear envelope begins to break down; centrioles move to opposite poles of the cell; and the mitotic spindle begins to form from the centrosomes. By the end of prophase, the chromosomes are fully condensed and the nuclear membrane has disappeared.",
            "Metaphase is the stage where chromosomes align at the cell's equator, called the metaphase plate. The spindle fibers attach to the kinetochores (protein structures on the centromeres) of each chromosome. The cell checks to ensure all chromosomes are properly attached to spindle fibers before proceeding—this is a critical checkpoint to prevent errors in chromosome distribution.",
            "Meiosis is a different type of cell division that produces four daughter cells, each with half the number of chromosomes as the parent cell. This process is essential for sexual reproduction and occurs only in specialized cells that produce gametes (sex cells): sperm in males and eggs in females. Meiosis involves two rounds of cell division (meiosis I and meiosis II) and includes crossing over, where genetic material is exchanged between homologous chromosomes, creating genetic diversity.",
            "Anaphase is characterized by the separation of sister chromatids. The spindle fibers shorten, pulling the sister chromatids apart toward opposite poles of the cell. Each chromatid is now considered an individual chromosome. The cell elongates during this phase. Anaphase is typically the shortest phase of mitosis.",
            "Telophase is essentially the reverse of prophase. The chromosomes begin to decondense back into chromatin; nuclear envelopes reform around each set of chromosomes, creating two nuclei; and the spindle apparatus disassembles. Cytokinesis, the physical division of the cytoplasm, usually begins during late telophase. In animal cells, a cleavage furrow forms and pinches the cell in two. In plant cells, a cell plate forms down the middle of the cell. The result is two genetically identical daughter cells.",
            "Apoptosis, also called programmed cell death, is a normal process where cells self-destruct in a controlled manner. It plays crucial roles in development (such as the formation of fingers and toes by eliminating cells between them) and in removing damaged or potentially cancerous cells. Unlike necrosis (uncontrolled cell death from injury), apoptosis is a regulated process that doesn't cause inflammation."
        ]
    },
    {
        "name": "Computer Architecture - Long Technical Docs",
        "question": "Explain the von Neumann architecture and its key components.",
        "context": [
            "The von Neumann architecture, named after mathematician and physicist John von Neumann, is a computer architecture design model that forms the basis of most modern computers. The architecture was first described in 1945 in a paper about the EDVAC (Electronic Discrete Variable Automatic Computer). The key innovation of the von Neumann architecture is the stored-program concept: both program instructions and data are stored in the same memory space, and the computer can modify its own program. This was revolutionary compared to earlier computers that were hardwired for specific tasks.",
            "The von Neumann architecture consists of five fundamental components: 1) The Central Processing Unit (CPU), which performs calculations and makes logical decisions. The CPU itself contains the Arithmetic Logic Unit (ALU) that performs mathematical and logical operations, and the Control Unit (CU) that directs the operation of the processor by fetching, decoding, and executing instructions. 2) Memory (also called storage or RAM), which holds both program instructions and data. In the von Neumann architecture, there is no distinction between instruction memory and data memory—they share the same address space.",
            "3) Input devices allow data and programs to be entered into the computer. Examples include keyboards, mice, scanners, microphones, and cameras. 4) Output devices allow the computer to communicate results to the user or other systems. Examples include monitors, printers, speakers, and network interfaces. 5) The Bus system, which provides communication pathways between the CPU, memory, and input/output devices. There are typically three types of buses: the data bus (transfers actual data), the address bus (carries memory addresses), and the control bus (carries control signals).",
            "Quantum computers represent a fundamentally different computing paradigm from von Neumann architecture. Instead of classical bits, quantum computers use quantum bits (qubits) that can exist in superposition—simultaneously representing multiple states. Quantum computers could potentially solve certain problems exponentially faster than classical computers, including factoring large numbers, simulating quantum systems, and optimizing complex systems. However, quantum computers are extremely difficult to build and maintain, requiring temperatures near absolute zero and sophisticated error correction.",
            "The von Neumann architecture has a fundamental limitation known as the 'von Neumann bottleneck.' Because instructions and data share the same bus and memory, the computer can either fetch instructions or read/write data, but not both simultaneously. This creates a bottleneck where the processor often sits idle waiting for data from memory. Modern computers attempt to mitigate this through various techniques: cache memory (small, fast memory close to the CPU), instruction pipelining (overlapping the execution of multiple instructions), branch prediction (guessing which instructions will be needed next), and multiple levels of cache (L1, L2, L3). Despite these optimizations, the fundamental bottleneck remains a limiting factor in computer performance.",
            "The fetch-decode-execute cycle (also called the instruction cycle) is the basic operation performed by the CPU: 1) Fetch: The Control Unit retrieves an instruction from memory at the address stored in the Program Counter (PC). The PC is then incremented to point to the next instruction. 2) Decode: The Control Unit interprets the instruction, determining what operation to perform and what operands are needed. 3) Execute: The ALU performs the operation, such as addition, subtraction, logical operations, or data movement. The results are stored in registers or memory. This cycle repeats continuously while the computer is running, billions of times per second in modern processors."
        ]
    },
    {
        "name": "Nutrition Science - Multiple Sources, Some Unrelated",
        "question": "What are the essential macronutrients and their functions?",
        "context": [
            "Macronutrients are nutrients that the body needs in large amounts to provide energy and support bodily functions. There are three primary macronutrients: carbohydrates, proteins, and fats. Each plays distinct and crucial roles in maintaining health.",
            "Carbohydrates are the body's primary and preferred source of energy. They are broken down into glucose, which cells use for immediate energy or store as glycogen in muscles and the liver. Carbohydrates are classified as simple (sugars like glucose, fructose, and sucrose) or complex (starches and fibers found in whole grains, legumes, and vegetables). The recommended dietary intake is typically 45-65% of total daily calories. Fiber, a type of carbohydrate that the body cannot digest, is essential for digestive health, helps regulate blood sugar levels, and promotes feelings of fullness. The brain relies almost exclusively on glucose for energy.",
            "The history of food preservation dates back thousands of years. Ancient civilizations used methods including drying, salting, smoking, and fermenting to preserve food for times of scarcity. The canning process was invented by Nicolas Appert in 1809. Refrigeration became widespread in the 20th century, revolutionizing food storage and distribution. Modern techniques include vacuum packaging, irradiation, and chemical preservatives.",
            "Proteins are composed of amino acids, often called the 'building blocks of life.' There are 20 different amino acids, nine of which are essential (must be obtained from diet) and 11 that are non-essential (the body can produce them). Proteins serve multiple critical functions: building and repairing tissues (muscles, skin, organs, hair, nails), producing enzymes and hormones, supporting immune function through antibodies, transporting molecules (like hemoglobin carrying oxygen), and providing energy when carbohydrates and fats are insufficient. Complete proteins (containing all essential amino acids) are found in animal products, while most plant proteins are incomplete (except quinoa, soy, and hemp). The recommended daily intake is about 0.8 grams per kilogram of body weight, though athletes and elderly individuals may need more.",
            "Fats (lipids) are essential for numerous bodily functions, despite often being unfairly maligned. Dietary fats serve several purposes: providing concentrated energy (9 calories per gram versus 4 for carbohydrates and proteins), absorbing fat-soluble vitamins (A, D, E, K), forming cell membranes, producing hormones, insulating organs, and supporting brain health (the brain is about 60% fat). There are different types of fats: Unsaturated fats (monounsaturated and polyunsaturated, including omega-3 and omega-6 fatty acids) are generally considered healthy and found in olive oil, avocados, nuts, seeds, and fatty fish. Saturated fats, found in animal products and tropical oils, should be consumed in moderation. Trans fats, found in some processed foods, should be avoided as they increase heart disease risk. Essential fatty acids (omega-3 and omega-6) must be obtained from diet as the body cannot produce them.",
            "The Mediterranean diet is a dietary pattern inspired by the traditional cuisines of Greece, Italy, and other Mediterranean countries. It emphasizes fruits, vegetables, whole grains, legumes, nuts, olive oil, and moderate amounts of fish and poultry, with limited red meat and dairy. Research shows that the Mediterranean diet is associated with reduced risk of heart disease, cancer, Parkinson's disease, and Alzheimer's disease. The diet is rich in anti-inflammatory compounds and antioxidants."
        ]
    },
    {
        "name": "Geology - Earth Layers with Mixed Content",
        "question": "What are the layers of the Earth and their characteristics?",
        "context": [
            "The Earth has a layered structure, divided into several distinct zones based on chemical composition and physical properties. From the outside in, the main layers are the crust, mantle, outer core, and inner core. Scientists have determined this structure through the study of seismic waves from earthquakes, which travel at different speeds through different materials.",
            "The crust is the outermost solid layer of the Earth and is the thinnest layer. There are two types: oceanic crust, which is 5-10 kilometers thick, denser, and composed primarily of basalt and gabbro; and continental crust, which is 30-50 kilometers thick (up to 70 km under mountain ranges), less dense, and composed primarily of granite and other lighter rocks. The crust and the uppermost part of the mantle together form the lithosphere, which is broken into tectonic plates that move over the asthenosphere below.",
            "The mantle lies beneath the crust and extends to about 2,900 kilometers depth, making it the thickest layer of the Earth (about 84% of Earth's volume). It is composed of silicate rocks rich in iron and magnesium. The mantle is divided into the upper mantle and lower mantle. Although solid, the mantle behaves plastically over geological timescales, flowing very slowly in convection currents. These convection currents are driven by heat from the core and radioactive decay, and they are the primary force behind plate tectonics. The asthenosphere, part of the upper mantle (approximately 100-200 km deep), is particularly plastic and allows tectonic plates to move.",
            "Volcanoes are openings in the Earth's crust through which molten rock (magma), ash, and gases erupt. There are several types of volcanoes: shield volcanoes (broad, gently sloping, formed by fluid lava), stratovolcanoes or composite volcanoes (steep-sided, formed by alternating layers of lava and ash), and cinder cone volcanoes (small, steep, formed from ejected lava fragments). The Ring of Fire, a horseshoe-shaped belt around the Pacific Ocean, contains about 75% of the world's active volcanoes due to the movement and collision of tectonic plates.",
            "The outer core extends from about 2,900 to 5,150 kilometers below the surface. It is composed primarily of liquid iron and nickel at extremely high temperatures (4,000-5,000°C). The liquid iron in the outer core flows due to convection currents, and this movement generates Earth's magnetic field through a process called the geodynamo. The magnetic field protects Earth from harmful solar radiation and cosmic rays, making it essential for life. Without this magnetic shield, solar wind would strip away the atmosphere.",
            "The inner core is a solid sphere with a radius of about 1,220 kilometers, composed primarily of iron and nickel. Despite temperatures reaching 5,000-6,000°C (as hot as the sun's surface), the inner core remains solid because of the immense pressure at the center of the Earth—about 3.6 million times atmospheric pressure at sea level. The inner core rotates slightly faster than the rest of the planet, a phenomenon discovered by studying seismic waves. The boundary between the inner and outer core is called the Bullen discontinuity."
        ]
    },
    {
        "name": "Art History - Renaissance with Distractors",
        "question": "What characterized Renaissance art and who were its major artists?",
        "context": [
            "The Renaissance was a period of cultural rebirth in Europe, spanning roughly from the 14th to the 17th century, beginning in Italy and spreading throughout Europe. Renaissance art represented a dramatic shift from the medieval period, characterized by a renewed interest in classical Greek and Roman culture, humanism, and naturalism.",
            "Key characteristics of Renaissance art include: Realism and naturalism—artists studied anatomy, proportion, and perspective to create more lifelike representations; Linear perspective—a mathematical system for creating the illusion of depth on a flat surface, developed by Filippo Brunelleschi and codified by Leon Battista Alberti; Chiaroscuro—the use of strong contrasts between light and dark to create volume and three-dimensionality; Sfumato—a subtle, almost imperceptible transition between colors and tones, perfected by Leonardo da Vinci; Humanism—focus on human experience, emotion, and individual dignity; Classical themes—subjects from Greek and Roman mythology alongside Christian themes; and Patronage—wealthy families like the Medici supported artists, leading to flourishing creativity.",
            "Leonardo da Vinci (1452-1519) epitomized the Renaissance ideal of the 'universal man' or polymath. He was not only a painter but also a scientist, inventor, mathematician, engineer, and anatomist. His most famous works include the Mona Lisa (known for its enigmatic expression and sfumato technique) and The Last Supper (a masterpiece of perspective and emotional drama). Leonardo's notebooks contain thousands of pages of observations, sketches, and inventions, demonstrating his insatiable curiosity and analytical mind.",
            "Impressionism was an art movement that emerged in France in the 1860s-1870s, characterized by small, thin brush strokes, emphasis on accurate depiction of light, ordinary subject matter, and unusual visual angles. Key Impressionist artists included Claude Monet, Pierre-Auguste Renoir, Edgar Degas, and Camille Pissarro. The movement was initially controversial, with critics deriding the style, but it eventually gained acceptance and profoundly influenced modern art.",
            "Michelangelo Buonarroti (1475-1564) is regarded as one of the greatest artists of all time. He excelled in sculpture, painting, architecture, and poetry. His sculptures include the David (a 17-foot marble masterpiece symbolizing the defense of civil liberties) and the Pietà (depicting Mary holding the dead Christ). His painting of the Sistine Chapel ceiling in Rome (1508-1512) is one of the most famous works in Western art, featuring scenes from Genesis including The Creation of Adam. Michelangelo's work exemplified terribilità—a sense of awe-inspiring grandeur and emotional intensity.",
            "Raphael Sanzio (1483-1520) was known for his harmonious and balanced compositions, as well as his skill in portraiture. His most famous works include The School of Athens (a fresco in the Vatican depicting great philosophers and scientists) and numerous Madonna paintings characterized by sweetness and serenity. Raphael synthesized the achievements of Leonardo and Michelangelo while developing his own graceful style. Despite his early death at 37, his influence on Western art was profound.",
            "Other important Renaissance artists included: Sandro Botticelli (The Birth of Venus, Primavera), known for his elegant, linear style and mythological subjects; Titian (Tiziano Vecellio), a master of color in the Venetian school; Albrecht Dürer, who brought Renaissance ideas to Northern Europe through his engravings and paintings; and Jan van Eyck, an early Northern Renaissance painter known for his detailed oil paintings and pioneering techniques."
        ]
    },
    {
        "name": "Sociology - Mixed Long Documents",
        "question": "What is social stratification and what are its major forms?",
        "context": [
            "Social stratification refers to a society's categorization of its people into rankings based on factors like wealth, income, education, occupation, and social status. It is a universal feature of society, though the specific form and degree of stratification vary across cultures and time periods. Stratification creates a hierarchy where some groups have more resources, power, and prestige than others. This hierarchy is generally reproduced across generations, as advantages and disadvantages tend to be inherited.",
            "The major forms of social stratification include: 1) Slavery, which is an extreme form where individuals are owned as property and have no personal freedom or rights. Though officially abolished in most countries, forms of slavery and human trafficking still exist. 2) Caste systems, where social position is ascribed at birth and remains fixed throughout life. The traditional Indian caste system, though legally abolished, still influences social relations. People in different castes were historically prohibited from intermarrying and had strictly defined occupations. The system was religiously justified and very rigid.",
            "3) Estate (feudal) systems were common in medieval Europe and other regions. Society was divided into distinct estates or orders with different rights, obligations, and lifestyles: the nobility (landowning aristocrats), the clergy (religious leaders), and the commoners (peasants and serfs who worked the land). Social mobility between estates was rare. The system was based on land ownership and obligations of service and loyalty. 4) Class systems, which characterize modern industrial and post-industrial societies, are ostensibly more fluid and based on achieved characteristics (though ascribed characteristics still matter significantly).",
            "The Protestant Reformation was a 16th-century religious movement that challenged the authority of the Catholic Church and led to the creation of Protestant churches. It began when Martin Luther posted his Ninety-Five Theses in 1517, criticizing church practices like the sale of indulgences. Other key figures included John Calvin, Huldrych Zwingli, and King Henry VIII of England, who broke with Rome to form the Church of England. The Reformation had profound religious, political, and social consequences throughout Europe.",
            "Class systems are based on economic factors but also include social and cultural dimensions. Karl Marx viewed class primarily in terms of relationship to the means of production: the bourgeoisie (owners of capital) and the proletariat (workers who sell their labor). Max Weber added status (prestige or honor) and party (political power) as additional dimensions of stratification, arguing that these don't always align with economic class. In contemporary society, sociologists often identify classes such as: upper class (wealthy elites with inherited wealth and/or very high incomes), upper-middle class (highly educated professionals and managers), middle class (white-collar workers, small business owners), working class (blue-collar workers, service workers), and lower class or underclass (those in poverty with limited opportunities).",
            "Social mobility refers to the movement of individuals or groups between different positions in the system of social stratification. Vertical mobility is movement up or down the hierarchy (upward or downward mobility). Horizontal mobility is movement between positions at the same level. Intergenerational mobility compares a person's status to their parents'. Intragenerational mobility is change within a person's lifetime. Structural mobility occurs when large-scale economic changes create opportunities for mobility. The American Dream embodies the belief in high upward mobility through hard work, but research shows that actual social mobility in the United States is lower than in many other developed nations, and class background strongly predicts outcomes."
        ]
    }
]

def prompt_test(question: str, context: dict):
    RAG_SYSTEM_PROMPT = """You are a precise and careful question-answering assistant. Your task is to answer questions based strictly on the provided source documents. Accuracy is your highest priority.
    Core Instructions
    1. Source Fidelity

    Answer ONLY using information explicitly stated in the provided documents
    Never introduce information from your training data or general knowledge
    If the documents don't contain enough information to answer fully, explicitly state what's missing
    Distinguish clearly between what the documents state directly versus what might be inferred

    2. Handling Uncertainty
    When you encounter any of these situations, you MUST acknowledge it:

    The documents don't address the question at all → State: "The provided documents do not contain information about [topic]."
    The documents only partially answer the question → State which parts you can answer and which parts are not covered
    The documents contain contradictory information → Point out the contradiction and present both viewpoints
    The documents are ambiguous or unclear → Note the ambiguity and provide the most reasonable interpretation while flagging uncertainty

    3. Citation and Attribution

    Reference specific sections, pages, or passages when answering
    Use phrases like "According to [document name/section]..." or "The document states that..."
    When synthesizing information from multiple parts of the documents, indicate all relevant sources
    If paraphrasing, stay as close to the original meaning as possible

    4. Answer Structure
    Provide answers in this format:

    Direct Answer: Start with a clear, concise answer if the information is available
    Supporting Evidence: Quote or closely paraphrase relevant passages from the documents
    Context: Add any necessary context from the documents that helps clarify the answer
    Limitations: Note any gaps, uncertainties, or caveats

    5. What NOT to Do

    ❌ Do not fill in gaps with external knowledge, even if you're confident it's correct
    ❌ Do not make assumptions or logical leaps beyond what the documents support
    ❌ Do not provide examples unless they appear in the source documents
    ❌ Do not say something is "likely" or "probably" true if the documents don't state it
    ❌ Do not provide background information not present in the documents, even for context

    6. Verification Checklist
    Before finalizing your answer, verify:

    Every claim can be traced back to the provided documents
    You've acknowledged any information gaps
    You've noted any assumptions or inferences you've made
    You've indicated confidence level where appropriate
    You've cited sources for key claims

    Document Context
    The following documents have been provided as your knowledge base:
    <DOCUMENTS>
    {documents}
    </DOCUMENTS>
    User Question
    {question}
    Your Response
    Provide your answer following the guidelines above. Prioritize accuracy over completeness—it's better to say "I don't know based on these documents" than to provide unsupported information.
    """

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    formatted_context = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(context["documents"][0])])

    result = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=RAG_SYSTEM_PROMPT.format(documents=formatted_context, question=question),
    )
    return {
        "answer": result.text,
        "sources": [
            {
                "chunk_id": context["ids"][0][i],
                "text_preview": doc[:150] + "...",
                "distance": context["distances"][0][i],
            }
            for i, doc in enumerate(context["documents"][0])
        ]
    }


def run_test_suite():
    """
    Run all test cases and display results.
    """
    print("=" * 80)
    print("RAG PROMPT TEST SUITE")
    print("=" * 80)
    print()
    
    results = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}/{len(TEST_CASES)}: {test_case['name']}")
        print(f"{'=' * 80}\n")
        
        print(f"Question: {test_case['question']}\n")
        
        print("Context:")
        for j, ctx in enumerate(test_case['context'], 1):
            print(f"  [{j}] {ctx[:100]}{'...' if len(ctx) > 100 else ''}")
        print()
        
        try:
            response = prompt_test(test_case['question'], test_case['context'])
            print(f"LLM Response:\n{response}\n")
            
            results.append({
                "test_name": test_case['name'],
                "question": test_case['question'],
                "status": "SUCCESS",
                "response": response
            })
            
        except Exception as e:
            error_msg = f"ERROR: {str(e)}"
            print(f"LLM Response:\n{error_msg}\n")
            
            results.append({
                "test_name": test_case['name'],
                "question": test_case['question'],
                "status": "FAILED",
                "error": str(e)
            })
        
        # Sleep for 1 second between API calls to avoid rate limits
        if i < len(TEST_CASES):  # Don't sleep after the last test
            print("Waiting 2 second before next test...")
            time.sleep(2)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for r in results if r["status"] == "SUCCESS")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print("\nFailed Tests:")
        for r in results:
            if r["status"] == "FAILED":
                print(f"  - {r['test_name']}: {r['error']}")
    
    return results


# Run the test suite
if __name__ == "__main__":
    results = run_test_suite()