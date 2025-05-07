import streamlit as st
import json
import requests
from streamlit_lottie import st_lottie

def load_lottie_url(url):
    """Load a Lottie animation from URL"""
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def load_lottie_file(filepath):
    """Load a Lottie animation from file"""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except:
        return None

# Predefined Lottie animations
ANIMATIONS = {
    "brain": "https://assets5.lottiefiles.com/packages/lf20_ystsffqy.json",
    "chat": "https://assets3.lottiefiles.com/packages/lf20_8wuout7s.json",
    "health": "https://assets9.lottiefiles.com/packages/lf20_5njp3vgg.json",
    "work": "https://assets1.lottiefiles.com/packages/lf20_0zblbeqy.json",
    "education": "https://assets1.lottiefiles.com/packages/lf20_jtbfg43t.json",
    "vision": "https://assets4.lottiefiles.com/packages/lf20_ikvz7qhc.json",
    "loading": "https://assets4.lottiefiles.com/packages/lf20_kk62um5v.json",
    "success": "https://assets7.lottiefiles.com/packages/lf20_s2lryxtd.json",
    "error": "https://assets4.lottiefiles.com/packages/lf20_qpwbiyxf.json"
}

def display_lottie_animation(animation_key, height=200, width=None):
    """Display a predefined Lottie animation"""
    if animation_key in ANIMATIONS:
        animation = load_lottie_url(ANIMATIONS[animation_key])
        if animation:
            st_lottie(animation, height=height, width=width, key=f"lottie_{animation_key}")
            return True
    return False

def display_brain_animation():
    """Display the brain animation"""
    display_lottie_animation("brain")

def display_loading_animation():
    """Display a loading animation"""
    display_lottie_animation("loading", height=100)

def display_success_animation():
    """Display a success animation"""
    display_lottie_animation("success", height=100)

def display_error_animation():
    """Display an error animation"""
    display_lottie_animation("error", height=100) 