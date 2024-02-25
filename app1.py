import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import graphviz
import tempfile

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def generate_course_structure(field_of_study):
    prompt = f'''As an expert in {field_of_study}, please provide the prerequisite structure for the courses. The format should be a dictionary where each key represents a course, and the value is a list of prerequisite courses. For example:
{{
    "Python Basics": [],
    "Intermediate Python": ["Python Basics"],
    "Advanced Python": ["Intermediate Python"],
    "Data Structures": ["Intermediate Python"],
    "Algorithms": ["Data Structures"],
    "Machine Learning": ["Data Structures", "Algorithms"]
}}
Please provide the prerequisite structure for {field_of_study}:'''
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text.strip("```")


def generate_course_roadmap(course_structure):
    # Create a Digraph object with custom styling
    dot = graphviz.Digraph(format='svg', graph_attr={'bgcolor': 'transparent'}, node_attr={'style': 'filled', 'fillcolor': '#F8F9FA', 'fontname': 'Arial', 'fontsize': '14', 'shape': 'rect', 'gradientangle': '90', 'penwidth': '2', 'margin': '0.25', 'fontcolor': '#333333', 'fixedsize': 'false'}, edge_attr={'color': '#666666', 'arrowhead': 'open', 'penwidth': '2'})

    for course, prerequisites in course_structure.items():

        label = f"{course}\nPrerequisites: {', '.join(prerequisites)}" if prerequisites else course

        dot.node(course, shape='rect', style='filled', fillcolor='#F8F9FA:#CEE3F6', label=label, tooltip=f"Click to learn more about {course}")

        for prereq in prerequisites:
            dot.node(prereq, shape='rect', style='filled', fillcolor='#F8F9FA:#F2CB05', label=prereq, tooltip=f"Click to learn more about {prereq}")
            dot.edge(prereq, course, color='#666666', style='solid')

    svg_content = dot.pipe().decode('utf-8')

    with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as f:
        f.write(svg_content.encode("utf-8"))
        svg_path = f.name

    return svg_path


st.title("Course Roadmap Generator")

field_of_study = st.text_input("Enter Field of Study", "")

if st.button("Generate Course Roadmap"):
    if field_of_study:
        course_structure = generate_course_structure(field_of_study)
        course_structure = eval(course_structure)
        svg_path = generate_course_roadmap(course_structure)
        st.image(svg_path)
    else:
        st.error("Please enter a field of study.")
