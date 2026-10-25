import os
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models import (
    User, Destination, Attraction, Package, PackageItinerary,
    Hotel, Room, Booking, Payment, Review, Favourite,
    BookingStatusHistory, RoomReservation
)

def run_seed():
    print("Beginning database seeding for TripNest...")

    # Create all tables if not exist
    db.create_all()

    # 1. Seed Demo Users
    if not User.query.filter_by(email='admin@tripnest.com').first():
        admin = User(
            full_name='TripNest Administrator',
            email='admin@tripnest.com',
            phone='+91 9876543210',
            role='admin'
        )
        admin.set_password('Admin@12345')
        db.session.add(admin)
        print("Created Admin user: admin@tripnest.com / Admin@12345")

    user_priya = User.query.filter_by(email='priya.sharma@example.com').first()
    if not user_priya:
        user_priya = User(
            full_name='Priya Sharma',
            email='priya.sharma@example.com',
            phone='+91 9811122334',
            role='customer'
        )
        user_priya.set_password('Customer@123')
        db.session.add(user_priya)
        print("Created Customer: priya.sharma@example.com / Customer@123")

    user_rahul = User.query.filter_by(email='rahul.verma@example.com').first()
    if not user_rahul:
        user_rahul = User(
            full_name='Rahul Verma',
            email='rahul.verma@example.com',
            phone='+91 9822233445',
            role='customer'
        )
        user_rahul.set_password('Customer@123')
        db.session.add(user_rahul)
        print("Created Customer: rahul.verma@example.com / Customer@123")

    db.session.commit()

    # Check if destinations already seeded
    if Destination.query.first():
        print("Destinations already populated. Skipping core destination seed.")
        return

    # 2. Indian Tourism Destinations Data
    destinations_data = [
        {
            "name": "Ooty",
            "country": "India",
            "region": "Tamil Nadu",
            "category": "Hill Station",
            "description": "Nestled in the Nilgiri Hills, Ooty is fondly known as the Queen of Hill Stations. Famous for verdant tea estates, panoramic viewpoints, eucalyptus aroma, and the UNESCO heritage Nilgiri Mountain Railway.",
            "image_url": "https://images.unsplash.com/photo-1589182373726-e4f658ab50f0?auto=format&fit=crop&w=1200&q=80",
            "estimated_budget": Decimal("15000.00"),
            "attractions": [
                {"name": "Government Botanical Garden", "fee": Decimal("50.00"), "open": "07:00 AM - 06:30 PM", "desc": "Sprawling 55-acre terraced garden featuring exotic flora and fossil tree trunks."},
                {"name": "Doddabetta Peak", "fee": Decimal("30.00"), "open": "09:00 AM - 06:00 PM", "desc": "Highest mountain in the Nilgiri Mountains with breathtaking valley vistas and telescope house."},
                {"name": "Pykara Lake & Waterfalls", "fee": Decimal("100.00"), "open": "08:30 AM - 05:30 PM", "desc": "Serene lake with exciting speedboat rides and cascading waterfalls amidst pine woods."}
            ],
            "packages": [
                {
                    "name": "Enchanting Nilgiris Explorer",
                    "duration": 4,
                    "price": Decimal("13999.00"),
                    "inclusions": "4-Star Hotel, Daily Breakfast & Dinner, Toy Train Experience, Private Cab Sightseeing",
                    "itinerary": [
                        (1, "Arrival & Ooty Lake", "Arrival at Coimbatore/Ooty, transfer to hotel. Afternoon boating at Ooty Lake and stroll along Charing Cross."),
                        (2, "Peak & Botanical Wonders", "Morning drive to Doddabetta Peak. Afternoon visit to the Government Botanical Garden and Rose Garden."),
                        (3, "Coonoor Tea Trails", "Toy train joyride to Coonoor. Visit Sim's Park, Dolphin's Nose, and authentic tea factory tour with tea tasting."),
                        (4, "Pykara & Departure", "Visit Pykara Falls and pine forest. Shopping for homemade chocolates followed by departure.")
                    ]
                }
            ],
            "hotels": [
                {
                    "name": "Savoy - IHCL SeleQtions Ooty",
                    "address": "77 Sylks Road, Ooty",
                    "rating": Decimal("4.8"),
                    "amenities": "Free WiFi, Fireplace, Luxury Spa, Colonial Dining, Mountain View, Valet Parking",
                    "rooms": [
                        ("Colonial Heritage Room", 2, Decimal("8500.00"), 6),
                        ("Executive Valley Suite", 3, Decimal("14500.00"), 4)
                    ]
                }
            ]
        },
        {
            "name": "Kodaikanal",
            "country": "India",
            "region": "Tamil Nadu",
            "category": "Hill Station",
            "description": "Known as the Princess of Hill Stations, Kodaikanal charms visitors with misty cliffs, cloud-capped hills, star-shaped Kodai lake, and cool forest trails.",
            "image_url": "https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=1200&q=80",
            "estimated_budget": Decimal("14000.00"),
            "attractions": [
                {"name": "Kodaikanal Lake", "fee": Decimal("40.00"), "open": "06:00 AM - 07:00 PM", "desc": "Artificial star-shaped lake surrounded by the Palani Hills, ideal for cycling and rowing."},
                {"name": "Pillar Rocks", "fee": Decimal("20.00"), "open": "09:00 AM - 04:30 PM", "desc": "Three giant rock pillars standing vertically at a majestic height of 400 feet."},
                {"name": "Coaker's Walk", "fee": Decimal("30.00"), "open": "07:00 AM - 07:00 PM", "desc": "One-kilometer pedestrian pathway constructed along the edge of steep mountain slopes."}
            ],
            "packages": [
                {
                    "name": "Misty Kodai Retreat",
                    "duration": 3,
                    "price": Decimal("10999.00"),
                    "inclusions": "Resort Accommodation, Campfire with Music, All Meals, Local Guide, Transfers",
                    "itinerary": [
                        (1, "Welcome to the Mist", "Check-in to hillside resort. Sunset stroll on Coaker's walk and evening by Kodai Lake."),
                        (2, "Rocks, Caves & Pine Forest", "Explore Pillar Rocks, Guna Caves, and serene walk through the heritage Pine Forest."),
                        (3, "Silver Cascade & Farewell", "Morning visit to Silver Cascade Waterfalls, spice shopping, and onward departure.")
                    ]
                }
            ],
            "hotels": [
                {
                    "name": "The Tamara Kodai",
                    "address": "La Providence, St Mary's Road, Kodaikanal",
                    "rating": Decimal("4.9"),
                    "amenities": "Heated Pool, Fine Dining, Spa, Mountain View Balconies, Library",
                    "rooms": [
                        ("Luxury Suite", 2, Decimal("11000.00"), 5),
                        ("Family Valley Cottage", 4, Decimal("18500.00"), 3)
                    ]
                }
            ]
        },
        {
            "name": "Munnar",
            "country": "India",
            "region": "Kerala",
            "category": "Hill Station",
            "description": "South India's tea capital, Munnar features rolling emerald hills, misty valleys, endangered Nilgiri Tahr at Eravikulam, and cascading spice plantations.",
            "image_url": "https://images.unsplash.com/photo-1596176530529-78163a4f7af2?auto=format&fit=crop&w=1200&q=80",
            "estimated_budget": Decimal("16500.00"),
            "attractions": [
                {"name": "Eravikulam National Park", "fee": Decimal("200.00"), "open": "07:30 AM - 04:00 PM", "desc": "Home to the rare Nilgiri Tahr and the highest peak in South India, Anamudi."},
                {"name": "Mattupetty Dam & Lake", "fee": Decimal("50.00"), "open": "09:30 AM - 05:00 PM", "desc": "Scenic reservoir flanked by tea estates with speedboating and horse riding."},
                {"name": "KDHP Tea Museum", "fee": Decimal("125.00"), "open": "09:00 AM - 04:00 PM", "desc": "Historic showcase of century-old tea manufacturing processes and live processing."}
            ],
            "packages": [
                {
                    "name": "Emerald Munnar Tea Odyssey",
                    "duration": 4,
                    "price": Decimal("14500.00"),
                    "inclusions": "Tea Plantation Villa Stay, Breakfast & Dinner, Safari in Eravikulam, Spice Garden Tour",
                    "itinerary": [
                        (1, "Scenic Drive & Cheeyappara", "Scenic drive from Kochi through Cheeyappara & Valara Waterfalls. Check-in to plantation villa."),
                        (2, "Wildlife & Highest Peaks", "Early morning safari in Eravikulam National Park. Afternoon visit to KDHP Tea Museum and factory."),
                        (3, "Dam, Lake & Echo Point", "Boating at Mattupetty Lake, shouts at Echo Point, and stroll around Kundala Dam lake."),
                        (4, "Spices & Return", "Visit herbal spice garden, purchase authentic spices and tea, transfer to airport/railway.")
                    ]
                }
            ],
            "hotels": [
                {
                    "name": "Fragrant Nature Munnar",
                    "address": "Bison Valley Road, Pothamedu, Munnar",
                    "rating": Decimal("4.8"),
                    "amenities": "Ayurvedic Spa, Fireplace, Free High-speed WiFi, Panoramic Deck, Tea Lounge",
                    "rooms": [
                        ("Tropic Green Room", 2, Decimal("7800.00"), 8),
                        ("Ocean & Valley Panoramic Suite", 3, Decimal("13200.00"), 4)
                    ]
                }
            ]
        },
        {
            "name": "Goa",
            "country": "India",
            "region": "Goa",
            "category": "Beach",
            "description": "Sun, sand, Portuguese heritage, and vibrant beach culture. Goa offers golden shorelines, UNESCO Baroque churches, buzzing nightlife, and delectable coastal seafood.",
            "image_url": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1200&q=80",
            "estimated_budget": Decimal("22000.00"),
            "attractions": [
                {"name": "Basilica of Bom Jesus", "fee": Decimal("0.00"), "open": "09:00 AM - 06:30 PM", "desc": "UNESCO World Heritage site holding the mortal remains of St. Francis Xavier."},
                {"name": "Aguada Fort & Lighthouse", "fee": Decimal("50.00"), "open": "09:30 AM - 06:00 PM", "desc": "17th-century Portuguese fortress overlooking Sinquerim Beach and Arabian Sea."},
                {"name": "Palolem Beach", "fee": Decimal("0.00"), "open": "24 Hours", "desc": "Crescent-shaped tropical beach lined with coconut palms and relaxed wooden shacks."}
            ],
            "packages": [
                {
                    "name": "Goan Sun, Sand & Heritage",
                    "duration": 5,
                    "price": Decimal("18999.00"),
                    "inclusions": "Beachfront Resort, Daily Buffet Breakfast, Sunset Mandovi River Cruise, South Goa Heritage Tour",
                    "itinerary": [
                        (1, "Arrival in Paradise", "Airport pickup, check-in to beach resort. Relax on the sandy beach with coastal cocktails."),
                        (2, "North Goa Beach Circuit", "Explore Calangute, Baga, and Fort Aguada. Watersports and beach cafe dinner."),
                        (3, "Old Goa & Latin Quarter", "Walk through Old Goa basilicas and colorful streets of Fontainhas heritage quarter."),
                        (4, "South Goa & Mandovi Cruise", "Visit Mangueshi Temple, Miramar beach, and 1-hour sunset cruise on Mandovi River with Goan folk dance."),
                        (5, "Flea Market & Departure", "Morning visit to Anjuna Flea Market / souvenir shopping followed by departure.")
                    ]
                }
            ],
            "hotels": [
                {
                    "name": "Taj Fort Aguada Resort & Spa",
                    "address": "Sinquerim, Candolim, Goa",
                    "rating": Decimal("4.9"),
                    "amenities": "Private Beach Access, Infinity Pool, Jiva Spa, Tennis Court, Multi-cuisine Dining",
                    "rooms": [
                        ("Superior Sea View Room", 2, Decimal("16000.00"), 10),
                        ("Luxury Heritage Villa", 4, Decimal("29000.00"), 4)
                    ]
                }
            ]
        },
        {
            "name": "Jaipur",
            "country": "India",
            "region": "Rajasthan",
            "category": "Heritage",
            "description": "The regal Pink City of Rajasthan showcases royal palaces, imposing hill forts, vibrant bazaars, and opulent Rajput architectural brilliance.",
            "image_url": "https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=1200&q=80",
            "estimated_budget": Decimal("19000.00"),
            "attractions": [
                {"name": "Amber Fort", "fee": Decimal("200.00"), "open": "08:00 AM - 05:30 PM", "desc": "Majestic hilltop fortress featuring Sheesh Mahal (Palace of Mirrors) and Maota Lake views."},
                {"name": "Hawa Mahal (Palace of Winds)", "fee": Decimal("50.00"), "open": "09:00 AM - 05:00 PM", "desc": "Iconic pink sandstone facade with 953 honeycomb windows designed for royal women."},
                {"name": "City Palace & Jantar Mantar", "fee": Decimal("300.00"), "open": "09:30 AM - 05:00 PM", "desc": "Royal residence complex and world's largest stone astronomical observatory."}
            ],
            "packages": [
                {
                    "name": "Royal Rajputana Grandeur",
                    "duration": 4,
                    "price": Decimal("16500.00"),
                    "inclusions": "Heritage Haveli Stay, Traditional Rajasthani Thali Dinner, Fort Sightseeing with Guide, Chokhi Dhani Entry",
                    "itinerary": [
                        (1, "Padharo Mhare Desh", "Arrive in Jaipur, traditional Rajasthani welcome. Evening cultural immersion at Chokhi Dhani."),
                        (2, "Forts of the Kings", "Full day tour of Amber Fort, Jaigarh Fort, and picturesque Jal Mahal palace."),
                        (3, "City Landmarks & Bazaars", "Visit Hawa Mahal, City Palace museum, Jantar Mantar, and shop in Johari Bazaar."),
                        (4, "Nahargarh & Farewell", "Sunrise at Nahargarh Fort overlooking Jaipur city, local handicrafts shopping, and airport drop.")
                    ]
                }
            ],
            "hotels": [
                {
                    "name": "ITC Rajputana, A Luxury Collection Hotel",
                    "address": "Palace Road, Gopalbari, Jaipur",
                    "rating": Decimal("4.8"),
                    "amenities": "Royal Courtyard, Outdoor Pool, Kaya Kalp Spa, Peshawri Cuisine, 24/7 Butler",
                    "rooms": [
                        ("Rajputana Executive Club", 2, Decimal("11500.00"), 8),
                        ("Thikana Royal Suite", 3, Decimal("21000.00"), 3)
                    ]
                }
            ]
        },
        {
            "name": "Manali",
            "country": "India",
            "region": "Himachal Pradesh",
            "category": "Hill Station",
            "description": "High-altitude Himalayan wonderland with snow-peaked Pir Panjal ranges, pine forests, adventure sports in Solang Valley, and spiritual retreats in Old Manali.",
            "image_url": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1200&q=80",
            "estimated_budget": Decimal("21000.00"),
            "attractions": [
                {"name": "Solang Valley", "fee": Decimal("0.00"), "open": "09:00 AM - 06:00 PM", "desc": "Adventure epicenter for paragliding, zorbing, quad biking, and winter skiing."},
                {"name": "Hadimba Temple", "fee": Decimal("0.00"), "open": "08:00 AM - 06:00 PM", "desc": "16th-century wooden pagoda temple built around a natural rock cave in Dhungri pine woods."},
                {"name": "Atal Tunnel & Sissu", "fee": Decimal("0.00"), "open": "24 Hours", "desc": "Engineering marvel leading to the magical Lahaul Valley and Sissu waterfall."}
            ],
            "packages": [
                {
                    "name": "Himalayan Snow & Thrill",
                    "duration": 5,
                    "price": Decimal("17500.00"),
                    "inclusions": "Pine Forest Resort, Daily Breakfast & Dinner, Atal Tunnel & Solang Excursion, Bonfire",
                    "itinerary": [
                        (1, "Scenic Drive into Himalayas", "Arrival via Kullu valley, check-in to chalet, evening at Mall Road."),
                        (2, "Solang Valley & Paragliding", "Full day adventure at Solang Valley. Paragliding, ropeway ride, and valley trek."),
                        (3, "Atal Tunnel & Lahaul Valley", "Cross the world-famous Atal Tunnel into snow-covered Sissu village and waterfall."),
                        (4, "Temples & Old Manali Cafes", "Visit Hadimba Devi temple, Vashisht hot springs, and indie cafes of Old Manali."),
                        (5, "Naggar Castle & Departure", "Explore Naggar Castle art gallery and river rafting at Beas River before departure.")
                    ]
                }
            ],
            "hotels": [
                {
                    "name": "The Himalayan Resort & Spa",
                    "address": "Hadimba Road, Manali",
                    "rating": Decimal("4.9"),
                    "amenities": "Gothic Castle Architecture, Heated Pool, Mountain Balconies, Pine Garden, Bar",
                    "rooms": [
                        ("Premier Castle Room", 2, Decimal("10500.00"), 6),
                        ("Himalayan Cottage", 4, Decimal("19500.00"), 3)
                    ]
                }
            ]
        },
        {
            "name": "Mysuru",
            "country": "India",
            "region": "Karnataka",
            "category": "Heritage",
            "description": "The cultural capital of Karnataka, celebrated for its spectacular illumination of the Mysore Palace, fragrant sandalwood, rich silk sarees, and royal heritage.",
            "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
            "estimated_budget": Decimal("12000.00"),
            "attractions": [
                {"name": "Mysore Palace (Amba Vilas)", "fee": Decimal("100.00"), "open": "10:00 AM - 05:30 PM", "desc": "Indo-Saracenic palace illuminated by 100,000 light bulbs every Sunday and festival evening."},
                {"name": "Chamundi Hills & Bull Temple", "fee": Decimal("0.00"), "open": "07:30 AM - 09:00 PM", "desc": "Hilltop temple dedicated to Goddess Chamundeshwari with monolithic Nandi bull."},
                {"name": "Brindavan Gardens", "fee": Decimal("50.00"), "open": "06:30 AM - 09:00 PM", "desc": "Terraced garden with musical fountains situated across the Krishnarajasagara dam."}
            ],
            "packages": [
                {
                    "name": "Mysuru Royal Heritage Trail",
                    "duration": 3,
                    "price": Decimal("8999.00"),
                    "inclusions": "Heritage Hotel Stay, Palace Guided Tour, Silk & Sandalwood Factory Visit, Daily Meals",
                    "itinerary": [
                        (1, "The Royal Welcome", "Arrive in Mysuru, explore Mysore Palace inside galleries and royal Durbar Hall."),
                        (2, "Chamundi Hills & Fountains", "Ascend Chamundi Hills, visit St. Philomena's Cathedral and evening illuminated Brindavan Gardens."),
                        (3, "Silk, Sweets & Departure", "Taste authentic Mysore Pak, visit silk weaving mills, and onward journey.")
                    ]
                }
            ],
            "hotels": [
                {
                    "name": "Radisson Blu Plaza Hotel Mysore",
                    "address": "MG Road, Mysuru",
                    "rating": Decimal("4.7"),
                    "amenities": "Pool overlooking Chamundi Hills, 24h Gymnasium, Fine Dining, Spa, Free WiFi",
                    "rooms": [
                        ("Deluxe Hill View Room", 2, Decimal("6500.00"), 10),
                        ("Business Executive Suite", 2, Decimal("11000.00"), 4)
                    ]
                }
            ]
        },
        {
            "name": "Alleppey (Alappuzha)",
            "country": "India",
            "region": "Kerala",
            "category": "Backwaters",
            "description": "The Venice of the East, famed for tranquil palm-fringed backwaters, traditional thatched houseboats (Kettuvallams), paddy fields, and serene village life.",
            "image_url": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=1200&q=80",
            "estimated_budget": Decimal("18000.00"),
            "attractions": [
                {"name": "Alleppey Backwaters Cruise", "fee": Decimal("1500.00"), "open": "08:00 AM - 05:30 PM", "desc": "Mesmerizing glide through canals, watching duck farming and rural village routines."},
                {"name": "Alappuzha Beach & Lighthouse", "fee": Decimal("20.00"), "open": "03:00 PM - 07:00 PM", "desc": "150-year-old historic pier extending into the Arabian Sea with sunset views."},
                {"name": "Marari Beach", "fee": Decimal("0.00"), "open": "24 Hours", "desc": "Pristine white sand fishing village beach dotted with quiet coconut groves."}
            ],
            "packages": [
                {
                    "name": "Luxury Houseboat Backwaters Cruise",
                    "duration": 3,
                    "price": Decimal("15999.00"),
                    "inclusions": "Overnight Premium Houseboat Cruise, All Traditional Kerala Meals with Karimeen, Shikara Ride",
                    "itinerary": [
                        (1, "Boarding the Kettuvallam", "12:00 PM check-in to private air-conditioned houseboat. Welcome tender coconut, cruise through Punnamada Lake."),
                        (2, "Canal Villages & Sunset", "Anchor near quiet paddy fields. Traditional lunch, evening canoeing through narrow canals, candlelight dinner."),
                        (3, "Sunrise & Marari Beach", "Sunrise cruise, checkout at 09:30 AM. Visit Marari beach before departure transfer.")
                    ]
                }
            ],
            "hotels": [
                {
                    "name": "Lake Palace Resort Alleppey",
                    "address": "Thirumala Ward, Chungam, Alappuzha",
                    "rating": Decimal("4.8"),
                    "amenities": "Island Resort on Lake Vembanad, Ayurvedic Spa, Water Taxi, Private Pool Villas",
                    "rooms": [
                        ("Lake View Villa", 2, Decimal("12500.00"), 5),
                        ("Private Pool Waterfront Cottage", 3, Decimal("22000.00"), 2)
                    ]
                }
            ]
        }
    ]

    for d_info in destinations_data:
        dest = Destination(
            name=d_info["name"],
            country=d_info["country"],
            region=d_info["region"],
            category=d_info["category"],
            description=d_info["description"],
            image_url=d_info["image_url"],
            estimated_budget=d_info["estimated_budget"],
            is_active=True
        )
        db.session.add(dest)
        db.session.flush()

        # Attractions
        for att in d_info.get("attractions", []):
            a = Attraction(
                destination_id=dest.id,
                name=att["name"],
                description=att["desc"],
                entry_fee=att["fee"],
                opening_information=att["open"]
            )
            db.session.add(a)

        # Packages
        for p in d_info.get("packages", []):
            pkg = Package(
                destination_id=dest.id,
                name=p["name"],
                description=f"Curated {p['duration']}-day expedition in {dest.name}. {p['inclusions']}",
                duration_days=p["duration"],
                price_per_person=p["price"],
                inclusions=p["inclusions"],
                image_url=dest.image_url,
                is_active=True
            )
            db.session.add(pkg)
            db.session.flush()

            for day_num, title, desc_text in p.get("itinerary", []):
                itin = PackageItinerary(
                    package_id=pkg.id,
                    day_number=day_num,
                    title=title,
                    description=desc_text
                )
                db.session.add(itin)

        # Hotels
        for h in d_info.get("hotels", []):
            hotel = Hotel(
                destination_id=dest.id,
                name=h["name"],
                address=h["address"],
                description=f"Premier luxury property in {dest.name} featuring state-of-the-art comforts, bespoke hospitality, and scenic location.",
                amenities=h["amenities"],
                rating=h["rating"],
                image_url=dest.image_url,
                is_active=True
            )
            db.session.add(hotel)
            db.session.flush()

            for r_type, cap, price, tot in h.get("rooms", []):
                room = Room(
                    hotel_id=hotel.id,
                    room_type=r_type,
                    capacity=cap,
                    price_per_night=price,
                    total_rooms=tot,
                    is_active=True
                )
                db.session.add(room)

    db.session.commit()
    print("Destinations, attractions, packages, and hotels seeded successfully!")

    # 3. Seed Sample Bookings, Payments, and Reviews
    user_p = User.query.filter_by(email='priya.sharma@example.com').first()
    ooty = Destination.query.filter_by(name='Ooty').first()
    ooty_pkg = Package.query.filter_by(destination_id=ooty.id).first()
    munnar = Destination.query.filter_by(name='Munnar').first()
    munnar_hotel = Hotel.query.filter_by(destination_id=munnar.id).first()
    munnar_room = Room.query.filter_by(hotel_id=munnar_hotel.id).first()

    if user_p and ooty_pkg:
        # Create a sample confirmed booking
        b1 = Booking(
            booking_reference='TN-2026-DEMO001',
            user_id=user_p.id,
            package_id=ooty_pkg.id,
            check_in=date.today() + timedelta(days=14),
            check_out=date.today() + timedelta(days=18),
            number_of_guests=2,
            total_amount=ooty_pkg.price_per_person * 2,
            booking_status='CONFIRMED',
            special_requests='Vegetarian meals requested, ground floor preferred.'
        )
        db.session.add(b1)
        db.session.flush()

        # Payment record
        pm1 = Payment(
            booking_id=b1.id,
            amount=b1.total_amount,
            payment_method='UPI Demo',
            transaction_reference='TXN-UPIDEMO-A98B76C123',
            payment_status='SUCCESS'
        )
        db.session.add(pm1)

        # Status History
        hist1 = BookingStatusHistory(
            booking_id=b1.id,
            old_status='PENDING',
            new_status='CONFIRMED',
            changed_by=user_p.id,
            remarks='Simulated UPI payment confirmed successfully.'
        )
        db.session.add(hist1)

        # Favourite
        f1 = Favourite(user_id=user_p.id, destination_id=ooty.id)
        f2 = Favourite(user_id=user_p.id, destination_id=munnar.id)
        db.session.add_all([f1, f2])

        # Review
        r1 = Review(
            user_id=user_p.id,
            destination_id=ooty.id,
            rating=5,
            comment="Ooty in autumn was absolutely magical! The Nilgiri Mountain Railway ride was unforgettable and the gardens were in full bloom. TripNest booking was completely seamless."
        )
        db.session.add(r1)

    if user_p and munnar_room:
        # Create a confirmed hotel booking with RoomReservations
        check_in = date.today() + timedelta(days=25)
        check_out = date.today() + timedelta(days=28)
        nights = (check_out - check_in).days

        b2 = Booking(
            booking_reference='TN-2026-DEMO002',
            user_id=user_p.id,
            room_id=munnar_room.id,
            check_in=check_in,
            check_out=check_out,
            number_of_guests=2,
            total_amount=munnar_room.price_per_night * Decimal(str(nights)),
            booking_status='CONFIRMED',
            special_requests='High floor with tea garden view please.'
        )
        db.session.add(b2)
        db.session.flush()

        pm2 = Payment(
            booking_id=b2.id,
            amount=b2.total_amount,
            payment_method='Card Demo',
            transaction_reference='TXN-CARDDEMO-F54E32D109',
            payment_status='SUCCESS'
        )
        db.session.add(pm2)

        # Allocate room reservations
        curr = check_in
        while curr < check_out:
            res = RoomReservation(
                booking_id=b2.id,
                room_id=munnar_room.id,
                reservation_date=curr,
                status='ACTIVE'
            )
            db.session.add(res)
            curr += timedelta(days=1)

        r2 = Review(
            user_id=user_p.id,
            destination_id=munnar.id,
            hotel_id=munnar_hotel.id,
            rating=5,
            comment="The tea plantation morning mist at Munnar was breathtaking. Hotel hospitality was world-class. Highly recommend reserving through TripNest!"
        )
        db.session.add(r2)

    db.session.commit()
    print("Sample bookings, payments, room reservations, and reviews seeded successfully!")
    print("TripNest database setup completed successfully!")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        run_seed()
