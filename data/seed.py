
system_prompt = """
**System Role:**
You are a "Typo & Vernacular Simulator" for the Indian Quick-Commerce market. Your goal is to take a correctly spelled grocery item and generate realistic search queries that users might type when looking for it.

**Context:**
Users in India often use:
1.  **Phonetic Spellings:** Typing Hindi/Malayalam/Tamil words in English script (e.g., "Dahi" instead of "Curd").
2.  **Transliteration Variations:** "Panir" vs "Paneer", "Biskut" vs "Biscuit".
3.  **Regional Slang:** "Thums Up" might be called "Coke" or "Cold drink".
4.  **Lazy Typing:** "Chkn" instead of "Chicken".

**Task:**
For each grocery item provided, generate 5 distinct search variations:
1.  **Variation_1 (Phonetic):** Misspelled based on sound (e.g., "Biscut").
2.  **Variation_2 (Vernacular):** The Hindi/Regional word in English script (e.g., "Aata" for "Wheat Flour").
3.  **Variation_3 (Regional/Manglish):** A specific South Indian phonetic variance if applicable (e.g., substituting 'p' for 'b' or 't' for 'd', like "Pisket").
4.  **Variation_4 (Hyper-Short):** Common abbreviation (e.g., "Soya chnk").
5.  **Variation_5 (Extreme):** A combination of vernacular + bad spelling (e.g., "Chana daal" -> "Channa dhal").

**Input Format:**
List of items: ["Maggi Noodles", "Amul Butter", "Tata Salt"]

**Output Format:**
Return ONLY a valid JSON object with the following structure:
{
  "items": [
    {
      "original": "Maggi Noodles",
      "variations": ["Magi nodles", "Megi", "Maida noodles", "Maggi 2 min", "Magee"]
    },
    ...
  ]
}
"""

SEED_PRODUCTS = [
    # --- DAIRY & BREAKFAST ---
    "Amul Pasteurized Butter", "Amul Cheese Slices", "Amul Taaza Toned Milk", 
    "Amul Masti Dahi", "Amul Malai Paneer", "Amul Ghee", "Amul Mithai Mate",
    "Nandini GoodLife Toned Milk", "Nandini Curd", "Nandini Ghee",
    "Milky Mist Paneer", "Milky Mist Greek Yogurt", "Mother Dairy Toned Milk",
    "Nestle A+ Nourish Milk", "Yakult Probiotic Drink",
    "Britannia 100% Whole Wheat Bread", "Modern White Sandwich Bread",
    "Amul Kool Cafe", "Cavins Milkshake", "Epigamia Greek Yogurt",

    # --- STAPLES & ATTAS ---
    "Aashirvaad Shudh Chakki Atta", "Aashirvaad Multigrain Atta",
    "Fortune Sunlite Refined Sunflower Oil", "Fortune Kachi Ghani Mustard Oil",
    "Fortune Soya Health Oil", "Saffola Gold Edible Oil", "Dhara Refined Vegetable Oil",
    "Tata Salt Vacuum Evaporated", "Tata Salt Lite", "Sendha Namak (Rock Salt)",
    "India Gate Basmati Rice Feast", "Daawat Rozana Basmati Rice", 
    "Fortune Mogra Basmati Rice", "Sona Masoori Rice", "Idli Rice",
    "Tata Sampann Unpolished Toor Dal", "Tata Sampann Moong Dal",
    "Tata Sampann Chana Dal", "Urad Gota (Whole White)", "Kabuli Chana",
    "Rajma Chitra", "Green Moong Dal", "Sugar (Loose)", "Jaggery Cubes (Gud)",

    # --- SNACKS & INSTANT FOOD ---
    "Maggi 2-Minute Masala Noodles", "Maggi Atta Noodles", "Sunfeast YiPPee! Magic Masala",
    "Top Ramen Curry Noodles", "Chings Secret Schezwan Noodles",
    "Knorr Tomato Soup", "Knorr Hot & Sour Vegetable Soup",
    "Kellogg's Corn Flakes Original", "Kellogg's Chocos", "Quaker Oats",
    "Saffola Masala Oats", "Yoga Bar Muesli", "Pintola Peanut Butter Crunchy",
    "Kissan Fresh Tomato Ketchup", "Maggi Hot & Sweet Tomato Chilli Sauce",
    "Chings Dark Soy Sauce", "Schezwan Chutney", "Kissan Mixed Fruit Jam",

    # --- BISCUITS & COOKIES ---
    "Parle-G Gold Biscuits", "Britannia Good Day Cashew", "Britannia Good Day Butter",
    "Britannia Marie Gold", "Britannia NutriChoice Digestive", "Britannia Little Hearts",
    "Sunfeast Dark Fantasy Choco Fills", "Oreo Vanilla Creme Biscuits",
    "Hide & Seek Chocolate Chip Cookies", "Monaco Salted Biscuits",
    "Unibic Assorted Cookies", "Karachi Bakery Fruit Biscuits",

    # --- CHIPS & NAMKEEN ---
    "Lays India's Magic Masala", "Lays American Style Cream & Onion", "Lays Classic Salted",
    "Kurkure Masala Munch", "Kurkure Solid Masti", "Bingo! Mad Angles Achaari Masti",
    "Doritos Nacho Cheese", "Pringles Sour Cream & Onion",
    "Haldiram's Aloo Bhujia", "Haldiram's Bhujia Sev", "Haldiram's Khatta Meetha",
    "Haldiram's Moong Dal", "Haldiram's Soan Papdi", "Bikano Bikaneri Bhujia",

    # --- BEVERAGES ---
    "Tata Tea Gold", "Tata Tea Premium", "Red Label Tea", "Taj Mahal Tea",
    "Wagh Bakri Premium Leaf Tea", "Organic India Tulsi Green Tea",
    "Nescafe Classic Instant Coffee", "Bru Instant Coffee", "Davidoff Rich Aroma Coffee",
    "Coca-Cola", "Thums Up", "Pepsi", "Sprite", "7 Up", "Fanta Orange",
    "Maaza Mango Drink", "Slice Mango Drink", "Frooti", "Paper Boat Aamras",
    "Real Fruit Power Mixed Fruit", "Tropicana 100% Orange Juice",
    "Bournvita Health Drink", "Horlicks Classic Malt", "Complan Royale Chocolate",
    "Bisleri Vedica Natural Mineral Water", "Kinley Soda",

    # --- CHOCOLATES & DESSERTS ---
    "Cadbury Dairy Milk Silk", "Cadbury Dairy Milk Fruit & Nut", "Cadbury Fuse",
    "Cadbury 5 Star", "Cadbury Gems", "KitKat Finger", "Munch Wafer",
    "Snickers Peanut Chocolate", "Ferrero Rocher", "Hershey's Chocolate Syrup",
    "Kwality Wall's Vanilla Ice Cream", "Amul Frostik Ice Cream",

    # --- SPICES (MASALAS) ---
    "Everest Garam Masala", "Everest Chicken Masala", "Everest Meat Masala",
    "Everest Chaat Masala", "Everest Tikhalal Chilli Powder", "Everest Turmeric Powder",
    "MDH Kitchen King Masala", "MDH Chana Masala", "MDH Sambar Masala",
    "Catch Table Salt Sprinkler", "Catch Black Pepper Sprinkler",
    "MTR Sambar Powder", "MTR Rasam Powder", "MTR Puliogare Paste",
    "Badshah Pav Bhaji Masala",

    # --- PERSONAL CARE ---
    "Dettol Original Soap", "Lifebuoy Total 10 Soap", "Dove Cream Beauty Bar",
    "Pears Pure & Gentle Soap", "Cinthol Original Soap", "Santoor Sandal & Turmeric",
    "Lux International Creamy Perfection", "Fiama Di Wills Gel Bar",
    "Colgate Strong Teeth Toothpaste", "Colgate MaxFresh Red Gel",
    "Pepsodent Germicheck", "Sensodyne Repair & Protect", "Dabur Red Paste",
    "Close Up Ever Fresh Red", "Listerine Mouthwash",
    "Clinic Plus Strong & Long Shampoo", "Head & Shoulders Cool Menthol",
    "Dove Intense Repair Shampoo", "Tressemme Keratin Smooth Shampoo",
    "Pantene Hair Fall Control", "Indulekha Bringha Oil", "Parachute Coconut Oil",
    "Nivea Men Dark Spot Reduction Face Wash", "Himalaya Purifying Neem Face Wash",
    "Garnier Men Acno Fight", "Ponds White Beauty Cream", "Fair & Lovely (Glow & Lovely)",
    "Whisper Ultra Clean", "Stayfree Secure Cottony Soft",

    # --- HOME CARE ---
    "Surf Excel Easy Wash Powder", "Surf Excel Matic Front Load Liquid",
    "Ariel Matic Top Load Powder", "Tide Plus Jasmine & Rose",
    "Vim Dishwash Bar", "Vim Lemon Dishwash Gel", "Pril Lime Liquid",
    "Lizol Floor Cleaner Citrus", "Domex Fresh Guard Toilet Cleaner",
    "Harpic Power Plus Toilet Cleaner", "Colin Glass Cleaner",
    "Comfort After Wash Fabric Conditioner", "Dettol Antiseptic Liquid",
    "Savlon Antiseptic Liquid", "Good Knight Gold Flash", "All Out Ultra Refill",
    "Hit Cockroach Killer Spray", "Odonil Room Freshener Block",
    "Duracell Ultra AA Batteries", "Scotch Brite Scrub Pad"
]
