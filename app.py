import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import graphviz
import tempfile

# Load environment variables
load_dotenv()

# Configure Generative AI API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def generate_course_structure(field_of_study):
    prompt = f'''Act as an expert academic advisor expert in {field_of_study}. Your task is to provide the steps to pursue the {field_of_study} in terms of topic need
    to be completed step-wise to excel in {field_of_study}. Please answer in the form of dictionary showing which step is prerequisite of which step to have a direction
    in the flowchart. Also, mention each and every topics to cover {field_of_study} with each steps. Please keep the format as - For example if the course is Mechanical Engineering, then the answer should be in the format-
    {{
    'Engineering Mathematics': {{
        'Prerequisite': 'High School Mathematics',
        'Topics': ['Linear Algebra', 'Calculus', 'Differential Equations', 'Vector Analysis', 'Complex Variables', 'Numerical Methods']
    }},
    'Physics': {{
        'Prerequisite': 'High School Physics',
        'Topics': ['Classical Mechanics', 'Heat and Thermodynamics', 'Electricity and Magnetism', 'Optics', 'Quantum Mechanics']
    }},
    'Materials Science': {{
        'Prerequisite': 'Physics',
        'Topics': ['Structure of Materials', 'Mechanical Properties of Materials', 'Thermal Properties of Materials', 'Electrical Properties of Materials', 'Magnetic Properties of Materials']
    }},
    'Solid Mechanics': {{
        'Prerequisite': ['Engineering Mathematics', 'Physics'],
        'Topics': ['Stress and Strain', 'Elasticity', 'Plasticity', 'Fracture Mechanics']
    }},
    'Fluid Mechanics': {{
        'Prerequisite': ['Engineering Mathematics', 'Physics'],
        'Topics': ['Fluid Statics', 'Fluid Dynamics', 'Heat Transfer', 'Mass Transfer']
    }},
    'Thermodynamics': {{
        'Prerequisite': ['Engineering Mathematics', 'Physics'],
        'Topics': ['First Law of Thermodynamics', 'Second Law of Thermodynamics', 'Third Law of Thermodynamics', 'Power Cycles']
    }},
    'Machine Design': {{
        'Prerequisite': ['Solid Mechanics', 'Materials Science'],
        'Topics': ['Design of Mechanical Elements', 'Design of Machine Systems']
    }},
    'Manufacturing Processes': {{
        'Prerequisite': ['Materials Science', 'Solid Mechanics'],
        'Topics': ['Casting', 'Forging', 'Machining', 'Welding', 'Additive Manufacturing']
    }},
    'Control Systems': {{
        'Prerequisite': ['Engineering Mathematics', 'Physics'],
        'Topics': ['Linear Control Systems', 'Nonlinear Control Systems', 'Robust Control Systems']
    }},
    'Mechatronics': {{
        'Prerequisite': ['Control Systems', 'Electronics'],
        'Topics': ['Sensors and Actuators', 'Embedded Systems', 'Robotics']
    }},
    'Computer-Aided Design (CAD)': {{
        'Prerequisite': ['Engineering Mathematics', 'Graphics'],
        'Topics': ['Solid Modeling', 'Parametric Modeling', 'Finite Element Analysis']
    }},
    'Finite Element Analysis (FEA)': {{
        'Prerequisite': ['Solid Mechanics', 'CAD'],
        'Topics': ['Theory of Finite Elements', 'Finite Element Software', 'Applications of FEA']
    }},
    'Computational Fluid Dynamics (CFD)': {{
        'Prerequisite': ['Fluid Mechanics', 'Numerical Methods'],
        'Topics': ['Theory of CFD', 'CFD Software', 'Applications of CFD']
    }}
    }}'''
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text


def generate_course_roadmap(course_structure):
    # Create a Digraph object with custom styling
    dot = graphviz.Digraph(format='svg', graph_attr={'bgcolor': 'transparent'}, node_attr={'style': 'filled', 'fillcolor': '#F8F9FA', 'fontname': 'Arial', 'fontsize': '14', 'shape': 'rect', 'gradientangle': '90', 'penwidth': '2', 'margin': '0.25', 'fontcolor': '#333333', 'fixedsize': 'false'}, edge_attr={'color': '#666666', 'arrowhead': 'open', 'penwidth': '2'})

    # Add nodes and edges based on the course structure dictionary
    for course, details in course_structure.items():
        # Extract prerequisite and topics information
        prerequisites = details.get('Prerequisite', '')
        topics = ', '.join(details.get('Topics', []))

        # Construct the label for the node
        label = f"{course}\nPrerequisite: {prerequisites}\nTopics: {topics}"

        # Add course node with tooltip
        dot.node(course, shape='rect', style='filled', fillcolor='#F8F9FA:#CEE3F6', label=label, tooltip=f"Click to learn more about {course}")

        # Add prerequisite nodes and edges
        if isinstance(prerequisites, list):
            for prereq in prerequisites:
                dot.node(prereq, shape='rect', style='filled', fillcolor='#F8F9FA:#F2CB05', label=prereq, tooltip=f"Click to learn more about {prereq}")
                dot.edge(prereq, course, color='#666666', style='solid')
        elif isinstance(prerequisites, str):
            dot.node(prerequisites, shape='rect', style='filled', fillcolor='#F8F9FA:#F2CB05', label=prerequisites, tooltip=f"Click to learn more about {prerequisites}")
            dot.edge(prerequisites, course, color='#666666', style='solid')

    # Render the graph to SVG content
    svg_content = dot.pipe().decode('utf-8')

    # Save the SVG content to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as f:
        f.write(svg_content.encode("utf-8"))
        svg_path = f.name

    # Display the SVG content
    return svg_path


# Streamlit UI
st.title("Course Roadmap Generator")

# Input field for the field of study
field_of_study = st.text_input("Enter Field of Study", "")

# Button to generate course roadmap
if st.button("Generate Course Roadmap"):
    if field_of_study:
        course_structure = generate_course_structure(field_of_study)
        course_structure = eval(course_structure)
        svg_path = generate_course_roadmap(course_structure)
        st.image(svg_path)
    else:
        st.error("Please enter a field of study.")
