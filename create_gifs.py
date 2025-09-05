#!/usr/bin/env python3
"""
Script to create GIFs showcasing the Organ Donor Chain UI/UX
Requires: pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os
import time

def create_ui_gif():
    """Create a GIF showcasing the UI components"""
    
    # Create frames for the GIF
    frames = []
    width, height = 800, 600
    
    # Colors
    bg_color = (102, 126, 234)  # Blue gradient start
    card_color = (255, 255, 255)  # White
    text_color = (45, 55, 72)  # Dark gray
    accent_color = (72, 187, 120)  # Green
    
    for i in range(10):
        # Create a new frame
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Draw background gradient effect
        for y in range(height):
            ratio = y / height
            r = int(bg_color[0] * (1 - ratio) + 118 * ratio)  # 118, 75, 162
            g = int(bg_color[1] * (1 - ratio) + 75 * ratio)
            b = int(bg_color[2] * (1 - ratio) + 162 * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Draw title
        try:
            font_large = ImageFont.truetype("arial.ttf", 36)
            font_medium = ImageFont.truetype("arial.ttf", 24)
            font_small = ImageFont.truetype("arial.ttf", 16)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Animated title
        title_y = 50 + int(10 * (i % 3))
        draw.text((width//2 - 150, title_y), "🏥 Organ Donor Chain", 
                 fill=card_color, font=font_large)
        
        # Draw cards with animation
        card_y = 150 + int(5 * (i % 2))
        
        # Card 1 - Donors
        draw.rounded_rectangle([50, card_y, 350, card_y + 120], 
                              radius=15, fill=card_color)
        draw.text((70, card_y + 20), "👥 View My Donors", 
                 fill=text_color, font=font_medium)
        draw.text((70, card_y + 50), "See all donors from your hospital", 
                 fill=text_color, font=font_small)
        
        # Card 2 - Patients
        draw.rounded_rectangle([400, card_y, 700, card_y + 120], 
                              radius=15, fill=card_color)
        draw.text((420, card_y + 20), "🏥 View My Patients", 
                 fill=text_color, font=font_medium)
        draw.text((420, card_y + 50), "Monitor patients waiting for transplants", 
                 fill=text_color, font=font_small)
        
        # Card 3 - Matches
        card_y2 = 300 + int(3 * (i % 2))
        draw.rounded_rectangle([225, card_y2, 525, card_y2 + 120], 
                              radius=15, fill=card_color)
        draw.text((245, card_y2 + 20), "💝 View My Matches", 
                 fill=text_color, font=font_medium)
        draw.text((245, card_y2 + 50), "Track successful organ donation matches", 
                 fill=text_color, font=font_small)
        
        # Add pulsing effect to buttons
        button_alpha = int(255 * (0.7 + 0.3 * (i % 3) / 2))
        button_color = (accent_color[0], accent_color[1], accent_color[2], button_alpha)
        
        # Draw buttons
        draw.rounded_rectangle([70, card_y + 80, 200, card_y + 105], 
                              radius=10, fill=accent_color)
        draw.text((100, card_y + 88), "View Donors", 
                 fill=card_color, font=font_small)
        
        draw.rounded_rectangle([420, card_y + 80, 550, card_y + 105], 
                              radius=10, fill=accent_color)
        draw.text((450, card_y + 88), "View Patients", 
                 fill=card_color, font=font_small)
        
        draw.rounded_rectangle([245, card_y2 + 80, 375, card_y2 + 105], 
                              radius=10, fill=accent_color)
        draw.text((275, card_y2 + 88), "View Matches", 
                 fill=card_color, font=font_small)
        
        frames.append(img)
    
    # Save as GIF
    frames[0].save('organ_donor_ui_demo.gif', 
                   save_all=True, 
                   append_images=frames[1:], 
                   duration=500, 
                   loop=0)
    
    print("✅ Created organ_donor_ui_demo.gif")

def create_login_flow_gif():
    """Create a GIF showing the login flow"""
    
    frames = []
    width, height = 600, 400
    
    # Colors
    bg_color = (102, 126, 234)
    form_color = (255, 255, 255)
    text_color = (45, 55, 72)
    button_color = (72, 187, 120)
    
    for i in range(8):
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Draw background gradient
        for y in range(height):
            ratio = y / height
            r = int(bg_color[0] * (1 - ratio) + 118 * ratio)
            g = int(bg_color[1] * (1 - ratio) + 75 * ratio)
            b = int(bg_color[2] * (1 - ratio) + 162 * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        try:
            font_large = ImageFont.truetype("arial.ttf", 28)
            font_medium = ImageFont.truetype("arial.ttf", 18)
            font_small = ImageFont.truetype("arial.ttf", 14)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Login form
        form_y = 80 + int(5 * (i % 2))
        draw.rounded_rectangle([100, form_y, 500, form_y + 240], 
                              radius=20, fill=form_color)
        
        # Title
        draw.text((200, form_y + 30), "🏥 Hospital Login", 
                 fill=text_color, font=font_large)
        
        # Form fields
        field_y = form_y + 80
        draw.rounded_rectangle([130, field_y, 470, field_y + 35], 
                              radius=8, fill=(248, 250, 252))
        draw.text((140, field_y + 10), "Email: hospital@example.com", 
                 fill=text_color, font=font_small)
        
        field_y += 50
        draw.rounded_rectangle([130, field_y, 470, field_y + 35], 
                              radius=8, fill=(248, 250, 252))
        draw.text((140, field_y + 10), "Password: ••••••••", 
                 fill=text_color, font=font_small)
        
        # Login button with animation
        button_y = field_y + 60
        button_alpha = int(255 * (0.8 + 0.2 * (i % 3) / 2))
        draw.rounded_rectangle([200, button_y, 400, button_y + 40], 
                              radius=10, fill=button_color)
        draw.text((280, button_y + 12), "Login", 
                 fill=form_color, font=font_medium)
        
        # Success message (appears after login)
        if i > 4:
            success_y = 50
            draw.rounded_rectangle([150, success_y, 450, success_y + 30], 
                                  radius=15, fill=(72, 187, 120))
            draw.text((250, success_y + 8), "✅ Login Successful!", 
                     fill=form_color, font=font_small)
        
        frames.append(img)
    
    # Save as GIF
    frames[0].save('login_flow_demo.gif', 
                   save_all=True, 
                   append_images=frames[1:], 
                   duration=800, 
                   loop=0)
    
    print("✅ Created login_flow_demo.gif")

def create_dashboard_gif():
    """Create a GIF showing the dashboard interface"""
    
    frames = []
    width, height = 900, 600
    
    # Colors
    bg_color = (102, 126, 234)
    card_color = (255, 255, 255)
    text_color = (45, 55, 72)
    stats_color = (72, 187, 120)
    
    for i in range(12):
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Draw background gradient
        for y in range(height):
            ratio = y / height
            r = int(bg_color[0] * (1 - ratio) + 118 * ratio)
            g = int(bg_color[1] * (1 - ratio) + 75 * ratio)
            b = int(bg_color[2] * (1 - ratio) + 162 * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        try:
            font_large = ImageFont.truetype("arial.ttf", 32)
            font_medium = ImageFont.truetype("arial.ttf", 20)
            font_small = ImageFont.truetype("arial.ttf", 14)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Header
        draw.text((width//2 - 200, 30), "🏥 Hospital Dashboard", 
                 fill=card_color, font=font_large)
        
        # Stats cards
        stats_y = 100 + int(3 * (i % 2))
        stats = [
            ("156", "Total Donors"),
            ("89", "Active Patients"),
            ("23", "Successful Matches"),
            ("12", "Partner Hospitals")
        ]
        
        for j, (number, label) in enumerate(stats):
            x = 50 + j * 200
            draw.rounded_rectangle([x, stats_y, x + 150, stats_y + 100], 
                                  radius=15, fill=stats_color)
            draw.text((x + 50, stats_y + 20), number, 
                     fill=card_color, font=font_large)
            draw.text((x + 20, stats_y + 60), label, 
                     fill=card_color, font=font_small)
        
        # Feature cards
        cards_y = 250 + int(2 * (i % 3))
        features = [
            ("👥 View My Donors", "See all donors from your hospital"),
            ("🏥 View My Patients", "Monitor patients waiting for transplants"),
            ("💝 View My Matches", "Track successful organ donation matches")
        ]
        
        for j, (title, desc) in enumerate(features):
            x = 50 + j * 280
            draw.rounded_rectangle([x, cards_y, x + 250, cards_y + 120], 
                                  radius=15, fill=card_color)
            draw.text((x + 20, cards_y + 20), title, 
                     fill=text_color, font=font_medium)
            draw.text((x + 20, cards_y + 50), desc, 
                     fill=text_color, font=font_small)
            
            # Animated button
            button_y = cards_y + 80
            button_alpha = int(255 * (0.7 + 0.3 * (i % 4) / 3))
            draw.rounded_rectangle([x + 20, button_y, x + 150, button_y + 30], 
                                  radius=8, fill=(72, 187, 120))
            draw.text((x + 50, button_y + 8), "View", 
                     fill=card_color, font=font_small)
        
        frames.append(img)
    
    # Save as GIF
    frames[0].save('dashboard_demo.gif', 
                   save_all=True, 
                   append_images=frames[1:], 
                   duration=600, 
                   loop=0)
    
    print("✅ Created dashboard_demo.gif")

if __name__ == "__main__":
    print("🎬 Creating UI/UX Demo GIFs...")
    print("📦 Make sure you have Pillow installed: pip install pillow")
    print()
    
    try:
        create_ui_gif()
        create_login_flow_gif()
        create_dashboard_gif()
        
        print()
        print("🎉 All GIFs created successfully!")
        print("📁 Files created:")
        print("   - organ_donor_ui_demo.gif")
        print("   - login_flow_demo.gif")
        print("   - dashboard_demo.gif")
        print()
        print("💡 You can now use these GIFs to showcase your UI/UX!")
        
    except ImportError:
        print("❌ Error: Pillow library not found!")
        print("📦 Install it with: pip install pillow")
    except Exception as e:
        print(f"❌ Error creating GIFs: {e}")
        print("💡 Make sure you have the required fonts installed")
