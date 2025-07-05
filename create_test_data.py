#!/usr/bin/env python3
"""
Script to create a small, meaningful test dataset for the Network Journal.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from backend.graph_service.connection import get_session_context
from backend.graph_service.people import create_person
from backend.graph_service.companies import create_company
from backend.graph_service.topics import create_topic
from backend.graph_service.events import create_event
from backend.graph_service.locations import create_location
from backend.graph_service.interactions import create_interaction
from shared.types import Company, Person, Topic, Event, Location, Interaction

def clear_database():
    """Clear all existing data from the database."""
    with get_session_context() as session:
        session.run("MATCH (n) DETACH DELETE n")
        print("✅ Cleared all existing data")

def create_test_data():
    """Create a small, meaningful test dataset."""
    
    # Create companies
    print("Creating companies...")
    acme_corp = create_company(Company(
        name="Acme Corp",
        industry="Technology",
        website="https://acme.com"
    ))
    
    tech_startup = create_company(Company(
        name="TechStart Inc",
        industry="Software",
        website="https://techstart.io"
    ))
    
    design_agency = create_company(Company(
        name="Creative Designs",
        industry="Design",
        website="https://creativedesigns.com"
    ))
    
    # Create locations
    print("Creating locations...")
    san_francisco = create_location(Location(
        city="San Francisco",
        state="CA",
        country="USA"
    ))
    
    new_york = create_location(Location(
        city="New York",
        state="NY",
        country="USA"
    ))
    
    # Create topics
    print("Creating topics...")
    ai_ml = create_topic(Topic(name="Artificial Intelligence"))
    web_dev = create_topic(Topic(name="Web Development"))
    design = create_topic(Topic(name="UI/UX Design"))
    entrepreneurship = create_topic(Topic(name="Entrepreneurship"))
    
    # Create events
    print("Creating events...")
    tech_conference = create_event(Event(
        name="Tech Innovation Summit",
        date="2025-07-15",
        type="conference",
        location_id=san_francisco.id
    ))
    
    startup_meetup = create_event(Event(
        name="Startup Networking Night",
        date="2025-06-30",
        type="meetup",
        location_id=new_york.id
    ))
    
    # Create people with relationships
    print("Creating people...")
    
    # Alice - Software Engineer at Acme Corp
    alice = create_person(Person(
        name="Alice Johnson",
        email="alice@acme.com",
        phone="+1-555-0101",
        linkedin_url="https://linkedin.com/in/alicejohnson",
        status="active",
        notes="Senior software engineer, interested in AI/ML"
    ))
    
    # Bob - Product Manager at TechStart
    bob = create_person(Person(
        name="Bob Smith",
        email="bob@techstart.io",
        phone="+1-555-0102",
        linkedin_url="https://linkedin.com/in/bobsmith",
        status="active",
        notes="Product manager with design background"
    ))
    
    # Carol - Designer at Creative Designs
    carol = create_person(Person(
        name="Carol Brown",
        email="carol@creativedesigns.com",
        phone="+1-555-0103",
        linkedin_url="https://linkedin.com/in/carolbrown",
        status="active",
        notes="UI/UX designer, passionate about user experience"
    ))
    
    # David - Entrepreneur
    david = create_person(Person(
        name="David Lee",
        email="david@startup.com",
        phone="+1-555-0104",
        linkedin_url="https://linkedin.com/in/davidlee",
        status="active",
        notes="Founder of multiple startups, mentor"
    ))
    
    # Eve - Developer at Acme Corp
    eve = create_person(Person(
        name="Eve Davis",
        email="eve@acme.com",
        phone="+1-555-0105",
        linkedin_url="https://linkedin.com/in/evedavis",
        status="active",
        notes="Full-stack developer, works with Alice"
    ))
    
    # Create interactions
    print("Creating interactions...")
    
    # Alice and Bob met at the tech conference
    alice_bob_interaction = create_interaction(Interaction(
        date="2025-07-15",
        channel="in_person",
        summary="Met at Tech Innovation Summit. Discussed potential collaboration on AI project."
    ))
    
    # Bob and Carol had a call about design work
    bob_carol_interaction = create_interaction(Interaction(
        date="2025-06-20",
        channel="call",
        summary="Discussed UI/UX design for new product feature. Carol provided valuable insights."
    ))
    
    # David and Alice had coffee
    david_alice_interaction = create_interaction(Interaction(
        date="2025-06-10",
        channel="in_person",
        summary="Coffee meeting to discuss startup mentorship opportunities. David offered to mentor Alice."
    ))
    
    # Eve and Alice work together
    eve_alice_interaction = create_interaction(Interaction(
        date="2025-06-25",
        channel="in_person",
        summary="Weekly team meeting. Discussed AI implementation for new feature."
    ))
    
    # Create relationships in the database
    print("Creating relationships...")
    with get_session_context() as session:
        # People -> Companies (WORKS_AT)
        session.run("""
            MATCH (p:Person {id: $person_id}), (c:Company {id: $company_id})
            CREATE (p)-[:WORKS_AT {role: $role, start_date: $start_date}]->(c)
        """, person_id=alice.id, company_id=acme_corp.id, role="Senior Software Engineer", start_date="2023-01-15")
        
        session.run("""
            MATCH (p:Person {id: $person_id}), (c:Company {id: $company_id})
            CREATE (p)-[:WORKS_AT {role: $role, start_date: $start_date}]->(c)
        """, person_id=bob.id, company_id=tech_startup.id, role="Product Manager", start_date="2024-03-01")
        
        session.run("""
            MATCH (p:Person {id: $person_id}), (c:Company {id: $company_id})
            CREATE (p)-[:WORKS_AT {role: $role, start_date: $start_date}]->(c)
        """, person_id=carol.id, company_id=design_agency.id, role="Senior UI/UX Designer", start_date="2022-08-10")
        
        session.run("""
            MATCH (p:Person {id: $person_id}), (c:Company {id: $company_id})
            CREATE (p)-[:WORKS_AT {role: $role, start_date: $start_date}]->(c)
        """, person_id=eve.id, company_id=acme_corp.id, role="Full-Stack Developer", start_date="2023-06-01")
        
        # People -> Topics (INTERESTED_IN)
        session.run("""
            MATCH (p:Person {id: $person_id}), (t:Topic {id: $topic_id})
            CREATE (p)-[:INTERESTED_IN]->(t)
        """, person_id=alice.id, topic_id=ai_ml.id)
        
        session.run("""
            MATCH (p:Person {id: $person_id}), (t:Topic {id: $topic_id})
            CREATE (p)-[:INTERESTED_IN]->(t)
        """, person_id=bob.id, topic_id=design.id)
        
        session.run("""
            MATCH (p:Person {id: $person_id}), (t:Topic {id: $topic_id})
            CREATE (p)-[:INTERESTED_IN]->(t)
        """, person_id=carol.id, topic_id=design.id)
        
        session.run("""
            MATCH (p:Person {id: $person_id}), (t:Topic {id: $topic_id})
            CREATE (p)-[:INTERESTED_IN]->(t)
        """, person_id=david.id, topic_id=entrepreneurship.id)
        
        session.run("""
            MATCH (p:Person {id: $person_id}), (t:Topic {id: $topic_id})
            CREATE (p)-[:INTERESTED_IN]->(t)
        """, person_id=eve.id, topic_id=web_dev.id)
        
        # People -> Events (ATTENDED)
        session.run("""
            MATCH (p:Person {id: $person_id}), (e:Event {id: $event_id})
            CREATE (p)-[:ATTENDED]->(e)
        """, person_id=alice.id, event_id=tech_conference.id)
        
        session.run("""
            MATCH (p:Person {id: $person_id}), (e:Event {id: $event_id})
            CREATE (p)-[:ATTENDED]->(e)
        """, person_id=bob.id, event_id=tech_conference.id)
        
        session.run("""
            MATCH (p:Person {id: $person_id}), (e:Event {id: $event_id})
            CREATE (p)-[:ATTENDED]->(e)
        """, person_id=david.id, event_id=startup_meetup.id)
        
        # People -> People (KNOWS)
        session.run("""
            MATCH (p1:Person {id: $person1_id}), (p2:Person {id: $person2_id})
            CREATE (p1)-[:KNOWS {strength: $strength, type: $type}]->(p2)
        """, person1_id=alice.id, person2_id=bob.id, strength=3, type="Colleague")
        
        session.run("""
            MATCH (p1:Person {id: $person1_id}), (p2:Person {id: $person2_id})
            CREATE (p1)-[:KNOWS {strength: $strength, type: $type}]->(p2)
        """, person1_id=alice.id, person2_id=eve.id, strength=5, type="Coworker")
        
        session.run("""
            MATCH (p1:Person {id: $person1_id}), (p2:Person {id: $person2_id})
            CREATE (p1)-[:KNOWS {strength: $strength, type: $type}]->(p2)
        """, person1_id=bob.id, person2_id=carol.id, strength=4, type="Business")
        
        session.run("""
            MATCH (p1:Person {id: $person1_id}), (p2:Person {id: $person2_id})
            CREATE (p1)-[:KNOWS {strength: $strength, type: $type}]->(p2)
        """, person1_id=alice.id, person2_id=david.id, strength=2, type="Mentor")
        
        # People -> Interactions (PARTICIPATED_IN)
        session.run("""
            MATCH (p:Person {id: $person_id}), (i:Interaction {id: $interaction_id})
            CREATE (p)-[:PARTICIPATED_IN]->(i)
        """, person_id=alice.id, interaction_id=alice_bob_interaction.id)
        
        session.run("""
            MATCH (p:Person {id: $person_id}), (i:Interaction {id: $interaction_id})
            CREATE (p)-[:PARTICIPATED_IN]->(i)
        """, person_id=bob.id, interaction_id=alice_bob_interaction.id)
        
        session.run("""
            MATCH (p:Person {id: $person_id}), (i:Interaction {id: $interaction_id})
            CREATE (p)-[:PARTICIPATED_IN]->(i)
        """, person_id=bob.id, interaction_id=bob_carol_interaction.id)
        
        session.run("""
            MATCH (p:Person {id: $person_id}), (i:Interaction {id: $interaction_id})
            CREATE (p)-[:PARTICIPATED_IN]->(i)
        """, person_id=carol.id, interaction_id=bob_carol_interaction.id)
        
        session.run("""
            MATCH (p:Person {id: $person_id}), (i:Interaction {id: $interaction_id})
            CREATE (p)-[:PARTICIPATED_IN]->(i)
        """, person_id=david.id, interaction_id=david_alice_interaction.id)
        
        session.run("""
            MATCH (p:Person {id: $person_id}), (i:Interaction {id: $interaction_id})
            CREATE (p)-[:PARTICIPATED_IN]->(i)
        """, person_id=alice.id, interaction_id=david_alice_interaction.id)
        
        session.run("""
            MATCH (p:Person {id: $person_id}), (i:Interaction {id: $interaction_id})
            CREATE (p)-[:PARTICIPATED_IN]->(i)
        """, person_id=eve.id, interaction_id=eve_alice_interaction.id)
        
        session.run("""
            MATCH (p:Person {id: $person_id}), (i:Interaction {id: $interaction_id})
            CREATE (p)-[:PARTICIPATED_IN]->(i)
        """, person_id=alice.id, interaction_id=eve_alice_interaction.id)
        
        # Events -> Locations (LOCATED_AT)
        session.run("""
            MATCH (e:Event {id: $event_id}), (l:Location {id: $location_id})
            CREATE (e)-[:LOCATED_AT]->(l)
        """, event_id=tech_conference.id, location_id=san_francisco.id)
        
        session.run("""
            MATCH (e:Event {id: $event_id}), (l:Location {id: $location_id})
            CREATE (e)-[:LOCATED_AT]->(l)
        """, event_id=startup_meetup.id, location_id=new_york.id)
    
    print("✅ Created test dataset with meaningful relationships!")

def main():
    """Main function to create the test dataset."""
    print("🧹 Clearing existing database...")
    clear_database()
    
    print("📊 Creating new test dataset...")
    create_test_data()
    
    print("\n🎉 Test dataset created successfully!")
    print("\nDataset includes:")
    print("- 5 people with realistic profiles")
    print("- 3 companies in different industries")
    print("- 4 topics of interest")
    print("- 2 events in different locations")
    print("- 2 locations (San Francisco, New York)")
    print("- 4 interactions between people")
    print("- Multiple relationship types: WORKS_AT, KNOWS, INTERESTED_IN, ATTENDED, PARTICIPATED_IN")
    
    print("\nThe network should now show a connected graph with meaningful relationships!")

if __name__ == "__main__":
    main() 