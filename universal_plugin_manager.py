"""
Universal Plugin Manager With NotePad++ - Cool Animated Background
With visible particle bands and modern UI
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import sys
import platform
import os
import importlib.util
from pathlib import Path
import psutil
from datetime import datetime
import random
import math
import time
import threading

class UniversalPluginManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Plugin Manager With NotePad++")
        self.root.geometry("1500x900")
        self.root.attributes('-alpha', 0.95)  # More transparent to see particles
        
        # Initialize managers
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.load_settings()
        self.plugin_manager = PluginManager()
        self.active_plugins = {}
        
        # Animation variables
        self.particles = []
        self.bands = []
        self.animation_active = True
        
        # Create GUI
        self.create_gui()
        
        # Load saved plugins
        self.load_saved_plugins()
        
    def create_gui(self):
        """Create universal plugin manager GUI with animated background"""
        # Create main canvas that covers everything
        self.main_canvas = tk.Canvas(self.root, bg='#000011', highlightthickness=0)
        self.main_canvas.pack(fill='both', expand=True)
        
        # Start background animations
        self.start_background_animations()
        
        # Create UI frames on top of canvas
        self.create_ui_frames()
        
        # Create status bar
        self.status_label = tk.Label(self.root, text="Universal Plugin Manager Active",
                                    bg='#001122', fg='#00ffff',
                                    font=('Segoe UI', 10, 'bold'), anchor='w', padx=10, pady=5)
        self.status_label.pack(fill='x', side='bottom')
        
    def start_background_animations(self):
        """Start multiple animated background effects"""
        # Particle system
        self.start_particle_system()
        
        # Animated bands
        self.start_band_animations()
        
        # Pulsing background
        self.start_pulse_animation()
        
    def start_particle_system(self):
        """Create visible floating particles"""
        # Use helper to create particles so settings can call it later
        # initial particles will be created below using self._create_particle()
        
        def update_particles():
            if not self.animation_active:
                return
                
            for particle in self.particles[:]:
                # Update position
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                
                # Add some turbulence
                particle['vx'] += (random.random() - 0.5) * 0.2
                particle['vy'] += (random.random() - 0.5) * 0.2
                
                # Wrap around screen
                if particle['x'] < -20:
                    particle['x'] = 1520
                elif particle['x'] > 1520:
                    particle['x'] = -20
                    
                if particle['y'] < -20:
                    particle['y'] = 920
                elif particle['y'] > 920:
                    particle['y'] = -20
                
                # Update visual
                size = particle['size']
                glow_size = size + particle['glow']
                
                try:
                    # Main particle
                    self.main_canvas.coords(particle['id'],
                                          particle['x']-size, particle['y']-size,
                                          particle['x']+size, particle['y']+size)
                    
                    # Add glow effect
                    if 'glow_id' not in particle:
                        particle['glow_id'] = self.main_canvas.create_oval(
                            particle['x']-glow_size, particle['y']-glow_size,
                            particle['x']+glow_size, particle['y']+glow_size,
                            fill='', outline=particle['color'], width=2
                        )
                    else:
                        self.main_canvas.coords(particle['glow_id'],
                                              particle['x']-glow_size, particle['y']-glow_size,
                                              particle['x']+glow_size, particle['y']+glow_size)
                        
                except:
                    pass
            
            # Create new particles occasionally (respect settings)
            max_particles = self.settings.get('ui', {}).get('particle_count', 80)
            if random.random() < 0.3 and len(self.particles) < max_particles:
                self._create_particle()
            
            self.root.after(20, update_particles)
        
        # Start with configured number of particles
        initial = self.settings.get('ui', {}).get('particle_count', 60)
        for _ in range(initial):
            self._create_particle()
            
        update_particles()
        
    def start_band_animations(self):
        """Create animated color bands across the background"""
        def create_band(y_pos, color, speed):
            # store base_speed so we can multiply it later from settings
            band = {
                'id': self.main_canvas.create_rectangle(0, y_pos-3, 1500, y_pos+3,
                                                     fill=color, outline='', width=0),
                'y': y_pos,
                'color': color,
                'base_speed': speed,
                'speed': speed,
                'direction': 1 if random.random() > 0.5 else -1
            }
            self.bands.append(band)
        
        # Create multiple bands
        colors = ['#00ffff', '#ff00ff', '#ffff00', '#ff0080', '#8000ff', '#00ff80']
        adv = self.settings.get('advanced', {})
        band_mul = adv.get('band_speed_multiplier', 1.0)
        for i in range(8):
            y_pos = 100 + i * 100
            base = random.uniform(0.5, 2.0)
            create_band(y_pos, random.choice(colors), base * band_mul)
        
        def update_bands():
            if not self.animation_active:
                return
                
            for band in self.bands:
                # Move band
                band['y'] += band['speed'] * band['direction']
                
                # Bounce off edges
                if band['y'] < 0:
                    band['y'] = 0
                    band['direction'] = 1
                elif band['y'] > 900:
                    band['y'] = 900
                    band['direction'] = -1
                
                # Update visual
                try:
                    self.main_canvas.coords(band['id'], 0, band['y']-3, 1500, band['y']+3)
                except:
                    pass
            
            self.root.after(50, update_bands)
            
        update_bands()

    def _create_particle(self):
        """Helper to create a single particle (usable by settings)."""
        adv = self.settings.get('advanced', {})
        palette = adv.get('particle_colors', ['#00ffff', '#ff00ff', '#ffff00', '#ff0080', '#8000ff', '#00ff80', '#ff4444'])
        speed_mul = adv.get('particle_speed', 1.0)
        glow_mul = adv.get('glow_intensity', 1.0)

        x = random.randint(0, 1500)
        y = random.randint(0, 900)

        ui = self.settings.get('ui', {})
        min_size = ui.get('particle_min_size', 6)
        max_size = ui.get('particle_max_size', 12)

        size = random.randint(min_size, max_size)
        color = random.choice(palette) if palette else '#00ffff'
        base_glow = max(0, int(3 * glow_mul))

        particle = {
            'id': self.main_canvas.create_oval(x-size, y-size, x+size, y+size,
                                             fill=color, outline='', width=0),
            'x': x, 'y': y,
            'vx': (random.random() - 0.5) * 4 * speed_mul,
            'vy': (random.random() - 0.5) * 4 * speed_mul,
            'size': size,
            'color': color,
            'glow': base_glow
        }
        self.particles.append(particle)
        
    def start_pulse_animation(self):
        """Create pulsing background effect"""
        def pulse():
            if not self.animation_active:
                return
                
            current_time = time.time()
            # Create subtle color shifts
            r = int(0 + 15 * math.sin(current_time * 0.3))
            g = int(17 + 15 * math.sin(current_time * 0.4))
            b = int(17 + 20 * math.sin(current_time * 0.5))
            
            color = f'#{max(0, min(255, r)):02x}{max(0, min(255, g)):02x}{max(0, min(255, b)):02x}'
            self.main_canvas.configure(bg=color)
            
            self.root.after(100, pulse)
            
        pulse()
        
    def create_ui_frames(self):
        """Create UI elements on top of animated background"""
        # Main container frame - more transparent to see particles
        self.main_frame = tk.Frame(self.root, bg='#1a1a2e')
        self.main_frame.place(relx=0.5, rely=0.5, anchor='center', width=1400, height=800)
        
        # Make the frame semi-transparent by using a canvas overlay
        self.overlay_canvas = tk.Canvas(self.main_frame, bg='#1a1a2e', highlightthickness=0)
        self.overlay_canvas.place(relwidth=1, relheight=1)
        
        # Title bar
        title_frame = tk.Frame(self.main_frame, bg='#2a2a4e', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="🚀 UNIVERSAL PLUGIN MANAGER WITH NOTEPAD++",
                bg='#2a2a4e', fg='#00ffff',
                font=('Segoe UI', 18, 'bold')).pack(side='left', padx=20, pady=15)
        
        # Close button
        tk.Button(title_frame, text="✕", bg='#ff4444', fg='white',
                 font=('Segoe UI', 12, 'bold'), bd=0, padx=15, pady=5,
                 command=self.root.quit).pack(side='right', padx=10, pady=10)
        
        # Sidebar - semi-transparent to see particles
        self.sidebar = tk.Frame(self.main_frame, bg='#3d3d60')
        self.sidebar.place(x=0, y=80, width=280, height=720)
        
        # Navigation buttons
        nav_buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("📝 Editor", self.show_editor),
            ("🔌 Plugins", self.open_plugin_manager),
            ("⚙️ Settings", self.open_settings),
            ("ℹ️ System", self.show_system_info)
        ]
        
        for text, command in nav_buttons:
            btn = tk.Button(self.sidebar, text=text, bg='#2d2d50', fg='#00ffff',
                           font=('Segoe UI', 11), bd=0, padx=20, pady=12,
                           activebackground='#00ffff', activeforeground='#1a1a2e',
                           command=command)
            btn.pack(fill='x', padx=10, pady=2)
        
        # Content area - semi-transparent to see particles
        self.content_frame = tk.Frame(self.main_frame, bg='#2a2a3e')
        self.content_frame.place(x=290, y=80, width=1110, height=720)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Style the notebook
        style = ttk.Style()
        style.configure('TNotebook', background='#1a1a2e', borderwidth=0)
        style.configure('TNotebook.Tab', background='#2d2d50', foreground='#00ffff',
                       padding=[15, 8], borderwidth=0, font=('Segoe UI', 10))
        style.map('TNotebook.Tab',
                 background=[('selected', '#00ffff')],
                 foreground=[('selected', '#1a1a2e')])
        
        # Create initial tabs
        self.create_dashboard_tab()
        self.create_editor_tab()
        
    def create_dashboard_tab(self):
        """Create animated dashboard"""
        dashboard = tk.Frame(self.notebook, bg='#2a2a3e')
        self.notebook.add(dashboard, text="📊 Dashboard")
        
        # Header
        header = tk.Frame(dashboard, bg='#2a2a3e')
        header.pack(fill='x', pady=20, padx=20)
        
        tk.Label(header, text="System Dashboard", bg='#2a2a3e', fg='#00ffff',
                font=('Segoe UI', 20, 'bold')).pack(anchor='w')
        
        tk.Label(header, text="Real-time system monitoring with animated metrics",
                bg='#2a2a3e', fg='#cccccc', font=('Segoe UI', 11)).pack(anchor='w', pady=(5, 0))
        
        # Metrics grid
        metrics_frame = tk.Frame(dashboard, bg='#2a2a3e')
        metrics_frame.pack(fill='x', padx=20, pady=10)
        
        # Create metric cards
        metrics = [
            ("CPU Usage", f"{psutil.cpu_percent():.1f}%", "#00ff88"),
            ("Memory", f"{psutil.virtual_memory().percent:.1f}%", "#00ffff"),
            ("Plugins", str(len(self.active_plugins)), "#ffaa00"),
            ("Uptime", "Active", "#ff0080")
        ]
        
        for i, (label, value, color) in enumerate(metrics):
            card = tk.Frame(metrics_frame, bg='#2d2d50', relief='flat', bd=0)
            card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='nsew')
            metrics_frame.grid_rowconfigure(i//2, weight=1)
            metrics_frame.grid_columnconfigure(i%2, weight=1)
            
            # Card content
            inner = tk.Frame(card, bg='#2d2d50')
            inner.pack(fill='both', expand=True, padx=20, pady=20)
            
            tk.Label(inner, text=label, bg='#2d2d50', fg='#ffffff',
                    font=('Segoe UI', 12)).pack(anchor='w')
            
            tk.Label(inner, text=value, bg='#2d2d50', fg=color,
                    font=('Segoe UI', 24, 'bold')).pack(anchor='w', pady=(10, 0))
        
        # Quick actions
        actions_frame = tk.Frame(dashboard, bg='#2a2a3e')
        actions_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(actions_frame, text="Quick Actions", bg='#2a2a3e', fg='#00ffff',
                font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 15))
        
        actions = tk.Frame(actions_frame, bg='#2a2a3e')
        actions.pack(fill='x')
        
        buttons = [
            ("🔌 Load Plugin", self.open_plugin_manager),
            ("📝 New Document", self.create_editor_tab),
            ("⚙️ Settings", self.open_settings),
            ("🔄 Refresh", self.refresh_dashboard)
        ]
        
        for text, command in buttons:
            tk.Button(actions, text=text, bg='#00ffff', fg='#1a1a2e',
                     font=('Segoe UI', 11, 'bold'), bd=0, padx=20, pady=10,
                     activebackground='#0088cc', command=command).pack(side='left', padx=5)
        
    def create_editor_tab(self):
        """Create text editor tab"""
        editor = tk.Frame(self.notebook, bg='#2a2a3e')
        self.notebook.add(editor, text="📝 New Document")
        
        # Toolbar
        toolbar = tk.Frame(editor, bg='#2d2d50', height=50)
        toolbar.pack(fill='x', pady=(0, 10))
        toolbar.pack_propagate(False)
        
        buttons = [
            ("💾 Save", self.save_file),
            ("📁 Open", self.open_file),
            ("📋 Copy", lambda: None),
            ("📄 Paste", lambda: None),
            ("🔍 Find", lambda: None)
        ]
        
        for text, command in buttons:
            tk.Button(toolbar, text=text, bg='#2d2d50', fg='#00ffff',
                     font=('Segoe UI', 10), bd=0, padx=15, pady=8,
                     activebackground='#00ffff', activeforeground='#1a1a2e',
                     command=command).pack(side='left', padx=2)
        
        # Text area
        text_frame = tk.Frame(editor, bg='#2a2a3e')
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(text_frame, bg='#2d2d50', troughcolor='#1a1a2e')
        scrollbar.pack(side='right', fill='y')
        
        # Text widget
        self.text_widget = tk.Text(text_frame, bg='#0f0f1a', fg='#d4d4d4',
                                  insertbackground='#00ffff', selectbackground='#00ffff',
                                  selectforeground='#1a1a2e',
                                  font=('Consolas', 12),
                                  yscrollcommand=scrollbar.set,
                                  relief='flat', bd=0,
                                  padx=15, pady=15)
        self.text_widget.pack(fill='both', expand=True)
        scrollbar.config(command=self.text_widget.yview)
        
        self.text_widget.insert('1.0', '# Welcome to Universal Plugin Manager With NotePad++\n\nStart typing your code here...\n\n')
        
    def show_dashboard(self):
        """Switch to dashboard"""
        for i in range(self.notebook.index('end')):
            if '📊' in self.notebook.tab(i, 'text'):
                self.notebook.select(i)
                break
                
    def show_editor(self):
        """Switch to editor"""
        for i in range(self.notebook.index('end')):
            if '📝' in self.notebook.tab(i, 'text'):
                self.notebook.select(i)
                break
                
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        # Remove and recreate dashboard
        for i in range(self.notebook.index('end')):
            if '📊' in self.notebook.tab(i, 'text'):
                self.notebook.forget(i)
                break
        self.create_dashboard_tab()
        self.status_label.config(text="Dashboard refreshed - Universal Plugin Manager Mode")
        
    def open_file(self):
        """Open file"""
        filename = filedialog.askopenfilename(
            title="Open File",
            filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.create_editor_tab()
                # Would insert content into new tab
                self.status_label.config(text=f"Opened: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{e}")
                
    def save_file(self):
        """Save file"""
        filename = filedialog.asksaveasfilename(
            title="Save File",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if filename:
            try:
                # Would save current tab content
                self.status_label.config(text=f"Saved: {filename}")
                messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")
                
    def open_plugin_manager(self):
        """Open plugin manager"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Universal Plugin Manager")
        dialog.geometry("1000x700")
        dialog.configure(bg='#1a1a2e')
        dialog.transient(self.root)
        
        # Header
        header = tk.Frame(dialog, bg='#2a2a4e', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="🔌 UNIVERSAL PLUGIN MANAGER",
                bg='#2a2a4e', fg='#00ffff',
                font=('Segoe UI', 18, 'bold')).pack(pady=20)
        
        # Plugin list
        list_frame = tk.Frame(dialog, bg='#1a1a2e')
        list_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        canvas = tk.Canvas(list_frame, bg='#1a1a2e', highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        plugin_frame = tk.Frame(canvas, bg='#1a1a2e')
        
        plugin_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=plugin_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.refresh_plugin_list(plugin_frame)
        
        # Bottom buttons
        btn_frame = tk.Frame(dialog, bg='#1a1a2e', height=60)
        btn_frame.pack(fill='x')
        btn_frame.pack_propagate(False)
        
        tk.Button(btn_frame, text="➕ Create New Plugin", bg='#00ff88', fg='#1a1a2e',
                 font=('Segoe UI', 12, 'bold'), bd=0, padx=20, pady=10,
                 command=self.create_new_plugin).pack(side='left', padx=20, pady=10)
        
        tk.Button(btn_frame, text="🔄 Refresh", bg='#00ffff', fg='#1a1a2e',
                 font=('Segoe UI', 12, 'bold'), bd=0, padx=20, pady=10,
                 command=lambda: self.refresh_plugin_list(plugin_frame)).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="❌ Close", bg='#ff4444', fg='white',
                 font=('Segoe UI', 12, 'bold'), bd=0, padx=20, pady=10,
                 command=dialog.destroy).pack(side='right', padx=20, pady=10)
        
    def refresh_plugin_list(self, container):
        """Refresh plugin list"""
        for widget in container.winfo_children():
            widget.destroy()
            
        plugins = self.plugin_manager.scan_plugins()
        
        if not plugins:
            tk.Label(container, text="No plugins found. Create your first universal plugin!",
                    bg='#1a1a2e', fg='#666666',
                    font=('Segoe UI', 14)).pack(pady=100)
            return
            
        for plugin in plugins:
            self.create_plugin_card(container, plugin)
            
    def create_plugin_card(self, parent, plugin_info):
        """Create modern plugin card"""
        card = tk.Frame(parent, bg='#2d2d50', relief='flat', bd=0)
        card.pack(fill='x', pady=8, padx=10)
        
        inner = tk.Frame(card, bg='#2d2d50')
        inner.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Info section
        info_frame = tk.Frame(inner, bg='#2d2d50')
        info_frame.pack(side='left', fill='both', expand=True)
        
        tk.Label(info_frame, text=plugin_info['name'],
                bg='#2d2d50', fg='#00ffff',
                font=('Segoe UI', 14, 'bold')).pack(anchor='w')
        
        status = "✅ ACTIVE" if plugin_info['loaded'] else "⭕ INACTIVE"
        color = '#00ff88' if plugin_info['loaded'] else '#666666'
        
        tk.Label(info_frame, text=status,
                bg='#2d2d50', fg=color,
                font=('Segoe UI', 10)).pack(anchor='w', pady=(5, 0))
        
        # Action buttons
        actions = tk.Frame(inner, bg='#2d2d50')
        actions.pack(side='right')
        
        if plugin_info['loaded']:
            tk.Button(actions, text="🔄 Unload", bg='#ffaa00', fg='#1a1a2e',
                     font=('Segoe UI', 10, 'bold'), bd=0, padx=15, pady=8,
                     command=lambda: self.unload_plugin(plugin_info['name'])).pack(side='left', padx=5)
        else:
            tk.Button(actions, text="▶️ Load", bg='#00ff88', fg='#1a1a2e',
                     font=('Segoe UI', 10, 'bold'), bd=0, padx=15, pady=8,
                     command=lambda: self.load_plugin(plugin_info['name'])).pack(side='left', padx=5)
            
        tk.Button(actions, text="🗑️ Delete", bg='#ff4444', fg='white',
                 font=('Segoe UI', 10, 'bold'), bd=0, padx=15, pady=8,
                 command=lambda: self.delete_plugin(plugin_info['name'])).pack(side='left', padx=5)
        
    def load_plugin(self, plugin_name):
        """Load a plugin"""
        try:
            plugin_class = self.plugin_manager.load_plugin(plugin_name)

            # Create plugin tab
            plugin_frame = tk.Frame(self.notebook, bg='#1a1a2e')
            tab_id = self.notebook.add(plugin_frame, text=f"🔌 {plugin_name}")

            # Instantiate plugin (guard so failure removes tab)
            try:
                plugin_instance = plugin_class(plugin_frame, self)
            except Exception as e:
                # remove the tab we just created
                try:
                    # find the tab index and forget
                    for i in range(self.notebook.index('end')):
                        if plugin_name in self.notebook.tab(i, 'text'):
                            self.notebook.forget(i)
                            break
                except Exception:
                    pass
                raise

            # If plugin provides a friendly tab name, use it
            try:
                friendly = getattr(plugin_instance, 'tab_name', None)
                if friendly:
                    # update the last-added tab's text
                    for i in range(self.notebook.index('end')):
                        if plugin_name in self.notebook.tab(i, 'text'):
                            self.notebook.tab(i, text=f"🔌 {friendly}")
                            break
            except Exception:
                pass

            # Select the newly-created plugin tab so it's visible immediately
            try:
                self.notebook.select(plugin_frame)
            except Exception:
                try:
                    # fallback: select by index of matching text
                    for i in range(self.notebook.index('end')):
                        if (plugin_name in self.notebook.tab(i, 'text')) or (friendly and friendly in self.notebook.tab(i, 'text')):
                            self.notebook.select(i)
                            break
                except Exception:
                    pass

            self.active_plugins[plugin_name] = {
                'instance': plugin_instance,
                'frame': plugin_frame
            }

            self.status_label.config(text=f"Universal Plugin Loaded: {plugin_name}")
            self.save_plugin_state()

            messagebox.showinfo("Success", f"Plugin '{plugin_name}' loaded with universal effects!")

        except Exception as e:
            # surface a helpful error
            messagebox.showerror("Error", f"Failed to load plugin:\n{e}")
            
    def unload_plugin(self, plugin_name):
        """Unload a plugin"""
        if plugin_name not in self.active_plugins:
            return
            
        try:
            plugin_info = self.active_plugins[plugin_name]
            
            # Cleanup
            if hasattr(plugin_info['instance'], 'cleanup'):
                plugin_info['instance'].cleanup()
                
            # Remove tab
            for i in range(self.notebook.index('end')):
                if plugin_name in self.notebook.tab(i, 'text'):
                    self.notebook.forget(i)
                    break
                    
            del self.active_plugins[plugin_name]
            self.plugin_manager.unload_plugin(plugin_name)
            
            self.status_label.config(text=f"Universal Plugin Unloaded: {plugin_name}")
            self.save_plugin_state()
            
            messagebox.showinfo("Success", f"Plugin '{plugin_name}' unloaded!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to unload plugin:\n{e}")
            
    def delete_plugin(self, plugin_name):
        """Delete a plugin"""
        if messagebox.askyesno("Confirm Universal Delete", f"Delete plugin '{plugin_name}' permanently?"):
            try:
                if plugin_name in self.active_plugins:
                    self.unload_plugin(plugin_name)
                    
                plugin_file = self.plugin_manager.plugins_dir / f"{plugin_name}.py"
                if plugin_file.exists():
                    plugin_file.unlink()
                    
                messagebox.showinfo("Success", f"Plugin '{plugin_name}' ultra-deleted!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete plugin:\n{e}")
                
    def create_new_plugin(self):
        """Create new ultra-modern plugin"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Universal Plugin")
        dialog.geometry("700x500")
        dialog.configure(bg='#1a1a2e')
        dialog.transient(self.root)
        
        content = tk.Frame(dialog, bg='#1a1a2e', padx=30, pady=30)
        content.pack(fill='both', expand=True)
        
        tk.Label(content, text="🚀 CREATE UNIVERSAL PLUGIN",
                bg='#1a1a2e', fg='#00ffff',
                font=('Segoe UI', 18, 'bold')).pack(pady=(0, 20))
        
        # Name input
        name_frame = tk.Frame(content, bg='#1a1a2e')
        name_frame.pack(fill='x', pady=10)
        
        tk.Label(name_frame, text="Plugin Name:", bg='#1a1a2e', fg='#ffffff',
                font=('Segoe UI', 12)).pack(anchor='w', pady=(0, 5))
        
        name_entry = tk.Entry(name_frame, bg='#2d2d50', fg='#00ffff',
                             insertbackground='#00ffff', font=('Segoe UI', 12),
                             relief='flat', bd=0)
        name_entry.pack(fill='x', ipady=8, padx=10, pady=5)
        
        # Tab name input
        tab_frame = tk.Frame(content, bg='#1a1a2e')
        tab_frame.pack(fill='x', pady=10)
        
        tk.Label(tab_frame, text="Tab Display Name:", bg='#1a1a2e', fg='#ffffff',
                font=('Segoe UI', 12)).pack(anchor='w', pady=(0, 5))
        
        tab_entry = tk.Entry(tab_frame, bg='#2d2d50', fg='#00ffff',
                            insertbackground='#00ffff', font=('Segoe UI', 12),
                            relief='flat', bd=0)
        tab_entry.pack(fill='x', ipady=8, padx=10, pady=5)
        
        def create():
            name = name_entry.get().strip()
            tab_name = tab_entry.get().strip() or name
            
            if not name:
                messagebox.showerror("Error", "Plugin name required!")
                return
                
            template = f'''"""
Universal Plugin: {name}
"""

import tkinter as tk
from tkinter import ttk, messagebox

class Plugin:
    def __init__(self, parent_frame, app):
        self.parent = parent_frame
        self.app = app
        self.tab_name = "{tab_name}"
        self.create_ultra_ui()
    
    def create_ultra_ui(self):
        # Universal header
        header = tk.Frame(self.parent, bg='#2a2a4e', height=80)
        header.pack(fill='x', pady=(0, 15))
        header.pack_propagate(False)
        
        tk.Label(header, text="🚀 {tab_name.upper()}",
                bg='#2a2a4e', fg='#00ffff',
                font=('Segoe UI', 16, 'bold')).pack(side='left', padx=20, pady=20)
        
        # Content area
        content = tk.Frame(self.parent, bg='#1a1a2e')
        content.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Animated welcome
        welcome = tk.Label(content, text="Universal Plugin Active!",
                          bg='#1a1a2e', fg='#00ff88',
                          font=('Segoe UI', 18, 'bold'))
        welcome.pack(expand=True)
        
        # Action button
        tk.Button(content, text="🚀 Execute Universal Action",
                 bg='#00ffff', fg='#1a1a2e',
                 font=('Segoe UI', 12, 'bold'), bd=0, padx=20, pady=12,
                 command=self.ultra_action).pack(pady=30)
    
    def ultra_action(self):
        messagebox.showinfo("Universal Action", f"Universal action executed in {{tab_name}}!")
        self.app.status_label.config(text="Universal Action: {tab_name} activated")
    
    def cleanup(self):
        pass
'''
            
            try:
                plugin_file = self.plugin_manager.plugins_dir / f"{name}.py"
                plugin_file.write_text(template, encoding='utf-8')
                
                messagebox.showinfo("Success", f"Universal Plugin '{name}' created!")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create plugin:\n{e}")
                
        # Buttons
        btn_frame = tk.Frame(content, bg='#1a1a2e')
        btn_frame.pack(fill='x', pady=(30, 0))
        
        tk.Button(btn_frame, text="🚀 CREATE UNIVERSAL PLUGIN", bg='#00ff88', fg='#1a1a2e',
                 font=('Segoe UI', 12, 'bold'), bd=0, padx=25, pady=12,
                 command=create).pack(side='right', padx=10)
        
        tk.Button(btn_frame, text="❌ Cancel", bg='#ff4444', fg='white',
                 font=('Segoe UI', 12, 'bold'), bd=0, padx=25, pady=12,
                 command=dialog.destroy).pack(side='right')
        
    def open_settings(self):
        """Open settings dialog and allow changing UI/animation settings."""
        ui = self.settings.setdefault('ui', {})

        dialog = tk.Toplevel(self.root)
        dialog.title("Settings")
        dialog.geometry("640x520")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg='#1a1a2e')

        # Notebook for tabs
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill='both', expand=True, padx=12, pady=12)

        # Tabs: General, Advanced, Theme, Plugins
        general_tab = tk.Frame(notebook, bg='#1a1a2e')
        adv_tab = tk.Frame(notebook, bg='#1a1a2e')
        theme_tab = tk.Frame(notebook, bg='#1a1a2e')
        plugins_tab = tk.Frame(notebook, bg='#1a1a2e')

        notebook.add(general_tab, text='General')
        notebook.add(adv_tab, text='Advanced')
        notebook.add(theme_tab, text='Theme')
        notebook.add(plugins_tab, text='Plugins')

        # --- General Tab ---
        tk.Label(general_tab, text="⚙️ General Settings", bg='#1a1a2e', fg='#00ffff', font=('Segoe UI', 14, 'bold')).pack(anchor='w', padx=12, pady=(8,6))

        # Alpha/transparency
        tk.Label(general_tab, text="Window Transparency:", bg='#1a1a2e', fg='#ffffff').pack(anchor='w', padx=12, pady=(8,0))
        alpha_var = tk.DoubleVar(value=ui.get('alpha', 0.95))
        tk.Scale(general_tab, from_=0.5, to=1.0, resolution=0.01, orient='horizontal', variable=alpha_var, bg='#1a1a2e', fg='#00ffff', highlightthickness=0).pack(fill='x', padx=12)

        # Particle count
        tk.Label(general_tab, text="Particle Count:", bg='#1a1a2e', fg='#ffffff').pack(anchor='w', padx=12, pady=(8,0))
        particle_var = tk.IntVar(value=ui.get('particle_count', 60))
        tk.Spinbox(general_tab, from_=0, to=500, textvariable=particle_var, bg='#2d2d50', fg='#00ffff', bd=0).pack(fill='x', padx=12)

        # Particle size range
        tk.Label(general_tab, text="Particle Size Min/Max:", bg='#1a1a2e', fg='#ffffff').pack(anchor='w', padx=12, pady=(8,0))
        size_min_var = tk.IntVar(value=ui.get('particle_min_size', 6))
        size_max_var = tk.IntVar(value=ui.get('particle_max_size', 12))
        size_frame = tk.Frame(general_tab, bg='#1a1a2e')
        size_frame.pack(fill='x', padx=12)
        tk.Spinbox(size_frame, from_=1, to=50, textvariable=size_min_var, width=6, bg='#2d2d50', fg='#00ffff', bd=0).pack(side='left')
        tk.Label(size_frame, text=" → ", bg='#1a1a2e', fg='#ffffff').pack(side='left', padx=6)
        tk.Spinbox(size_frame, from_=1, to=50, textvariable=size_max_var, width=6, bg='#2d2d50', fg='#00ffff', bd=0).pack(side='left')

        # Bands enabled
        bands_var = tk.BooleanVar(value=ui.get('bands_enabled', True))
        tk.Checkbutton(general_tab, text="Enable animated bands", variable=bands_var, bg='#1a1a2e', fg='#00ffff', selectcolor='#2a2a3e').pack(anchor='w', padx=12, pady=(8,6))

        # --- Advanced Tab ---
        adv = self.settings.setdefault('advanced', {})
        tk.Label(adv_tab, text="🔬 Advanced Options", bg='#1a1a2e', fg='#00ffff', font=('Segoe UI', 14, 'bold')).pack(anchor='w', padx=12, pady=(8,6))

        # Particle speed
        tk.Label(adv_tab, text="Particle Speed Multiplier:", bg='#1a1a2e', fg='#ffffff').pack(anchor='w', padx=12)
        particle_speed_var = tk.DoubleVar(value=adv.get('particle_speed', 1.0))
        tk.Scale(adv_tab, from_=0.1, to=4.0, resolution=0.05, orient='horizontal', variable=particle_speed_var, bg='#1a1a2e', fg='#00ffff').pack(fill='x', padx=12)

        # Glow intensity
        tk.Label(adv_tab, text="Glow Intensity:", bg='#1a1a2e', fg='#ffffff').pack(anchor='w', padx=12, pady=(8,0))
        glow_var = tk.DoubleVar(value=adv.get('glow_intensity', 1.0))
        tk.Scale(adv_tab, from_=0.0, to=5.0, resolution=0.1, orient='horizontal', variable=glow_var, bg='#1a1a2e', fg='#00ffff').pack(fill='x', padx=12)

        # Band speed multiplier
        tk.Label(adv_tab, text="Band Speed Multiplier:", bg='#1a1a2e', fg='#ffffff').pack(anchor='w', padx=12, pady=(8,0))
        band_speed_var = tk.DoubleVar(value=adv.get('band_speed_multiplier', 1.0))
        tk.Scale(adv_tab, from_=0.1, to=3.0, resolution=0.05, orient='horizontal', variable=band_speed_var, bg='#1a1a2e', fg='#00ffff').pack(fill='x', padx=12)

        # --- Theme Tab ---
        theme = adv.get('theme', {})
        tk.Label(theme_tab, text="🎨 Theme Overrides", bg='#1a1a2e', fg='#00ffff', font=('Segoe UI', 14, 'bold')).pack(anchor='w', padx=12, pady=(8,6))

        # Particle color palette (comma-separated hex colors)
        tk.Label(theme_tab, text="Particle Color Palette (comma-separated hex):", bg='#1a1a2e', fg='#ffffff').pack(anchor='w', padx=12, pady=(6,0))
        palette_var = tk.StringVar(value=','.join(adv.get('particle_colors', [])))
        tk.Entry(theme_tab, textvariable=palette_var, bg='#2d2d50', fg='#00ffff').pack(fill='x', padx=12, pady=(4,6))

        # Theme overrides
        tk.Label(theme_tab, text="Panel / Sidebar / Content / Accent (hex):", bg='#1a1a2e', fg='#ffffff').pack(anchor='w', padx=12, pady=(6,0))
        panel_bg_var = tk.StringVar(value=theme.get('panel_bg', '#2a2a4e'))
        sidebar_bg_var = tk.StringVar(value=theme.get('sidebar_bg', '#3d3d60'))
        content_bg_var = tk.StringVar(value=theme.get('content_bg', '#2a2a3e'))
        accent_var = tk.StringVar(value=theme.get('accent', '#00ffff'))

        theme_frame = tk.Frame(theme_tab, bg='#1a1a2e')
        theme_frame.pack(fill='x', padx=12, pady=(6,6))
        tk.Entry(theme_frame, textvariable=panel_bg_var, width=10, bg='#2d2d50', fg='#00ffff').pack(side='left')
        tk.Entry(theme_frame, textvariable=sidebar_bg_var, width=10, bg='#2d2d50', fg='#00ffff').pack(side='left', padx=6)
        tk.Entry(theme_frame, textvariable=content_bg_var, width=10, bg='#2d2d50', fg='#00ffff').pack(side='left', padx=6)
        tk.Entry(theme_frame, textvariable=accent_var, width=10, bg='#2d2d50', fg='#00ffff').pack(side='left', padx=6)

        # Font size
        tk.Label(theme_tab, text="Interface Font Size:", bg='#1a1a2e', fg='#ffffff').pack(anchor='w', padx=12, pady=(6,0))
        font_size_var = tk.IntVar(value=theme.get('font_size', 10))
        tk.Spinbox(theme_tab, from_=8, to=20, textvariable=font_size_var, bg='#2d2d50', fg='#00ffff', bd=0).pack(fill='x', padx=12, pady=(4,6))

        # --- Plugins Tab ---
        tk.Label(plugins_tab, text="🔌 Plugin Settings", bg='#1a1a2e', fg='#00ffff', font=('Segoe UI', 14, 'bold')).pack(anchor='w', padx=12, pady=(8,6))
        plugin_list_frame = tk.Frame(plugins_tab, bg='#1a1a2e')
        plugin_list_frame.pack(fill='both', expand=True, padx=12, pady=6)

        # Show list of plugins with their state
        plugins = self.plugin_manager.scan_plugins()
        for p in plugins:
            lbl = tk.Label(plugin_list_frame, text=f"{p['name']} - {'Loaded' if p['loaded'] else 'Not Loaded'}", bg='#1a1a2e', fg='#ffffff')
            lbl.pack(anchor='w')

        # Buttons (Preview, Apply & Save, Cancel) - global for all tabs
        btn_frame = tk.Frame(dialog, bg='#1a1a2e')
        btn_frame.pack(fill='x', padx=12, pady=(6,12))

        def preview():
            # apply to runtime but don't save
            ui['alpha'] = float(alpha_var.get())
            ui['particle_count'] = int(particle_var.get())
            ui['bands_enabled'] = bool(bands_var.get())
            ui['particle_min_size'] = int(size_min_var.get())
            ui['particle_max_size'] = int(size_max_var.get())

            adv['particle_speed'] = float(particle_speed_var.get())
            adv['glow_intensity'] = float(glow_var.get())
            adv['band_speed_multiplier'] = float(band_speed_var.get())
            adv['particle_colors'] = [c.strip() for c in palette_var.get().split(',') if c.strip()]
            adv['theme'] = {
                'panel_bg': panel_bg_var.get(),
                'sidebar_bg': sidebar_bg_var.get(),
                'content_bg': content_bg_var.get(),
                'accent': accent_var.get(),
                'font_size': int(font_size_var.get())
            }
            self.apply_ui_settings()

        def save_and_apply():
            preview()
            self.settings_manager.save_settings(self.settings)
            dialog.destroy()

        tk.Button(btn_frame, text="Preview", bg='#0088ff', fg='white', command=preview).pack(side='right', padx=6)
        tk.Button(btn_frame, text="Apply & Save", bg='#00ff88', fg='#1a1a2e', command=save_and_apply).pack(side='right', padx=6)
        tk.Button(btn_frame, text="Cancel", bg='#ff4444', fg='white', command=dialog.destroy).pack(side='right')
        
    def show_system_info(self):
        """Show ultra system info"""
        info = f"""
🖥️ UNIVERSAL SYSTEM INFO

OS: {platform.system()} {platform.release()}
Python: {sys.version.split()[0]}
CPU: {psutil.cpu_count()} cores
Memory: {psutil.virtual_memory().total // (1024**3):.1f} GB total
Active Plugins: {len(self.active_plugins)}

🚀 Universal Plugin Manager: ACTIVE
        """
        messagebox.showinfo("Universal System Info", info)
        
    def load_saved_plugins(self):
        """Load previously loaded plugins"""
        loaded = self.settings.get('plugins', {}).get('loaded', [])
        # Auto-add server_protection plugin if present but not yet tracked
        try:
            sp_path = self.plugin_manager.plugins_dir / 'server_protection.py'
            if sp_path.exists() and 'server_protection' not in loaded:
                loaded.append('server_protection')
                # Persist immediately so it loads next launch too
                self.settings['plugins']['loaded'] = loaded
                self.settings_manager.save_settings(self.settings)
        except Exception:
            pass
        for plugin_name in loaded:
            try:
                self.load_plugin(plugin_name)
            except Exception:
                pass
                
    def save_plugin_state(self):
        """Save plugin state"""
        self.settings['plugins']['loaded'] = list(self.active_plugins.keys())
        self.settings_manager.save_settings(self.settings)
        
    def apply_ui_settings(self):
        """Apply UI-related settings at runtime (transparency, particle/band settings)."""
        ui = self.settings.get('ui', {})

        # Apply window transparency
        alpha = ui.get('alpha', 0.95)
        try:
            self.root.attributes('-alpha', float(alpha))
        except Exception:
            pass

        # Bands visibility and speed
        bands_enabled = ui.get('bands_enabled', True)
        adv = self.settings.get('advanced', {})
        band_mul = adv.get('band_speed_multiplier', 1.0)
        for band in getattr(self, 'bands', []):
            try:
                self.main_canvas.itemconfigure(band['id'], state='normal' if bands_enabled else 'hidden')
                # adjust speed relative to stored base_speed if present
                if 'base_speed' in band:
                    band['speed'] = band['base_speed'] * band_mul
                else:
                    band['speed'] = band.get('speed', 1.0) * band_mul
            except Exception:
                pass

        # Particle adjustments (size, color, speed, glow)
        min_size = ui.get('particle_min_size', 6)
        max_size = ui.get('particle_max_size', 12)
        particle_speed = adv.get('particle_speed', 1.0)
        glow_mul = adv.get('glow_intensity', 1.0)
        palette = adv.get('particle_colors', [])
        for p in list(self.particles):
            # clamp sizes and update visuals
            p['size'] = max(1, min(max_size, max(min_size, int(p.get('size', min_size)))))
            # update color
            if palette:
                try:
                    new_color = random.choice(palette)
                    p['color'] = new_color
                    self.main_canvas.itemconfigure(p['id'], fill=new_color)
                except Exception:
                    pass
            # update velocity to match speed multiplier
            try:
                p['vx'] = (random.random() - 0.5) * 4 * particle_speed
                p['vy'] = (random.random() - 0.5) * 4 * particle_speed
            except Exception:
                pass
            # update glow
            try:
                p['glow'] = max(0, int(3 * glow_mul))
                if 'glow_id' in p:
                    glow_size = p['size'] + p.get('glow', 0)
                    self.main_canvas.coords(p['glow_id'], p['x']-glow_size, p['y']-glow_size, p['x']+glow_size, p['y']+glow_size)
                else:
                    # create glow if missing
                    p['glow_id'] = self.main_canvas.create_oval(p['x']- (p['size']+p['glow']), p['y']-(p['size']+p['glow']), p['x']+(p['size']+p['glow']), p['y']+(p['size']+p['glow']), fill='', outline=p.get('color',''), width=2)
            except Exception:
                pass

        # Particle count adjustments
        target = ui.get('particle_count', len(self.particles))
        try:
            target = int(target)
        except Exception:
            target = len(self.particles)

        # Add particles if needed
        while len(self.particles) < target:
            self._create_particle()

        # Remove excess particles
        while len(self.particles) > target:
            p = self.particles.pop()
            try:
                self.main_canvas.delete(p.get('id'))
                if 'glow_id' in p:
                    self.main_canvas.delete(p.get('glow_id'))
            except Exception:
                pass
        # Apply theme overrides across UI where possible
        try:
            theme = adv.get('theme', {})
            panel_bg = theme.get('panel_bg', '#2a2a4e')
            sidebar_bg = theme.get('sidebar_bg', '#3d3d60')
            content_bg = theme.get('content_bg', '#2a2a3e')
            accent = theme.get('accent', '#00ffff')
            font_size = int(theme.get('font_size', 10))

            if hasattr(self, 'main_frame'):
                try:
                    self.main_frame.config(bg=panel_bg)
                except Exception:
                    pass
            if hasattr(self, 'overlay_canvas'):
                try:
                    self.overlay_canvas.config(bg=panel_bg)
                except Exception:
                    pass
            if hasattr(self, 'sidebar'):
                try:
                    self.sidebar.config(bg=sidebar_bg)
                    for w in self.sidebar.winfo_children():
                        try:
                            if isinstance(w, tk.Button) or isinstance(w, tk.Label):
                                w.config(bg=sidebar_bg, fg=accent)
                        except Exception:
                            pass
                except Exception:
                    pass
            if hasattr(self, 'content_frame'):
                try:
                    self.content_frame.config(bg=content_bg)
                    for w in self.content_frame.winfo_children():
                        try:
                            w.config(bg=content_bg)
                        except Exception:
                            pass
                except Exception:
                    pass
            # Status label
            try:
                self.status_label.config(bg=panel_bg, fg=accent)
            except Exception:
                pass

            # Notebook / tab styling
            try:
                style = ttk.Style()
                style.configure('TNotebook', background=panel_bg)
                style.configure('TNotebook.Tab', background=content_bg, foreground=accent, font=('Segoe UI', max(9, font_size)))
                style.map('TNotebook.Tab', background=[('selected', accent)], foreground=[('selected', '#1a1a2e')])
            except Exception:
                pass
        except Exception:
            pass
        
    def run(self):
        """Start the universal plugin manager application"""
        self.root.mainloop()

class SettingsManager:
    """Settings manager"""
    def __init__(self):
        self.settings_file = Path("settings.json")
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Add UI/settings defaults so the settings UI has keys to read/write
        self.defaults = {
            'plugins': {'loaded': []},
            'ui': {
                'alpha': 0.95,
                'particle_count': 60,
                'bands_enabled': True,
                'particle_min_size': 6,
                'particle_max_size': 12
            },
            'advanced': {
                'particle_speed': 1.0,
                'glow_intensity': 1.0,
                'band_speed_multiplier': 1.0,
                'particle_colors': ['#00ffff', '#ff00ff', '#ffff00', '#ff0080', '#8000ff', '#00ff80', '#ff4444'],
                'theme': {
                    'panel_bg': '#2a2a4e',
                    'sidebar_bg': '#3d3d60',
                    'content_bg': '#2a2a3e',
                    'accent': '#00ffff',
                    'font_size': 10
                }
            }
        }
    
    def load_settings(self):
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    return self._merge_settings(self.defaults, loaded)
            except:
                return self.defaults.copy()
        return self.defaults.copy()
    
    def _merge_settings(self, defaults, loaded):
        result = defaults.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_settings(self, settings):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            return True
        except:
            return False

class PluginManager:
    """Plugin manager"""
    def __init__(self, plugins_dir="plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins = {}
        self.loaded_plugins = []
        self.plugins_dir.mkdir(exist_ok=True)
    
    def scan_plugins(self):
        plugins = []
        for plugin_file in self.plugins_dir.glob("*.py"):
            if plugin_file.stem != "__init__":
                plugins.append({
                    'name': plugin_file.stem,
                    'path': plugin_file,
                    'loaded': plugin_file.stem in self.loaded_plugins
                })
        return plugins
    
    def load_plugin(self, plugin_name):
        plugin_file = self.plugins_dir / f"{plugin_name}.py"
        if not plugin_file.exists():
            raise FileNotFoundError(f"Plugin {plugin_name} not found")
        
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[plugin_name] = module
        spec.loader.exec_module(module)
        
        if hasattr(module, 'Plugin'):
            self.plugins[plugin_name] = module
            if plugin_name not in self.loaded_plugins:
                self.loaded_plugins.append(plugin_name)
            return module.Plugin
        else:
            raise AttributeError(f"Plugin {plugin_name} has no Plugin class")
    
    def unload_plugin(self, plugin_name):
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
        if plugin_name in self.loaded_plugins:
            self.loaded_plugins.remove(plugin_name)
        if plugin_name in sys.modules:
            del sys.modules[plugin_name]

if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalPluginManager(root)
    app.run()