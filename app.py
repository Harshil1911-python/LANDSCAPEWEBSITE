from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, re, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = "dubai_landscape_secret_2026"
UPLOAD = "static/uploads"
os.makedirs(UPLOAD, exist_ok=True)
ALLOWED = {"png","jpg","jpeg","gif","webp","ico","mp4","webm","mov"}
DB_PATH = "database.db"

def db():
    c = sqlite3.connect(DB_PATH); c.row_factory = sqlite3.Row; return c

def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY, company_name TEXT DEFAULT 'TECHSERENIA',
            hero_title TEXT DEFAULT 'Turn Your Dubai Outdoor Space into an Exclusive Oasis',
            hero_subtitle TEXT DEFAULT 'Luxury landscape design and swimming pools by experts',
            logo TEXT DEFAULT '', bg_type TEXT DEFAULT 'image', bg_file TEXT DEFAULT '', favicon TEXT DEFAULT '',
            whatsapp TEXT DEFAULT '971500000000', phone TEXT DEFAULT '', email TEXT DEFAULT '',
            address TEXT DEFAULT '', map_url TEXT DEFAULT '', instagram TEXT DEFAULT '', facebook TEXT DEFAULT '',
            founder_name TEXT DEFAULT 'Founder Name', founder_title TEXT DEFAULT 'Founder & CEO',
            founder_desc TEXT DEFAULT 'Passionate about creating beautiful outdoor spaces across Dubai.',
            founder_image TEXT DEFAULT '', services_bg TEXT DEFAULT '',
            admin_pass TEXT DEFAULT '', delete_pass TEXT DEFAULT '',
            stat_projects TEXT DEFAULT '150', stat_years TEXT DEFAULT '12', stat_satisfaction TEXT DEFAULT '98', stat_team TEXT DEFAULT '25', stat_happy TEXT DEFAULT '200', stat_reviews TEXT DEFAULT '180',
            counters_bg TEXT DEFAULT '', faq_image TEXT DEFAULT '', faq_heading TEXT DEFAULT 'Some General Question?', cta_bg TEXT DEFAULT '', form_title TEXT DEFAULT 'Transform Your Dream Landscape with a Tailored Consultation', form_subtitle TEXT DEFAULT 'Book a private, one-on-one consultation with Dubai''s leading landscaping experts to explore a bespoke outdoor design tailored to your villa and lifestyle.', form_heading TEXT DEFAULT 'Schedule Your Free Consultation',
            smtp_sender TEXT DEFAULT '', smtp_app_pass TEXT DEFAULT '', smtp_receiver TEXT DEFAULT '',
            intro_title TEXT DEFAULT 'Green Space Landscaping Services',
            intro_text TEXT DEFAULT 'We believe outdoor spaces should be sanctuaries that nurture well-being and celebrate nature.',
            intro_image TEXT DEFAULT '', intro_badge TEXT DEFAULT '6+', intro_badge_label TEXT DEFAULT 'Year Experience',
            show_services INTEGER DEFAULT 1, show_about INTEGER DEFAULT 1, show_founder INTEGER DEFAULT 1,
            show_testimonials INTEGER DEFAULT 1, show_faqs INTEGER DEFAULT 1, show_gallery INTEGER DEFAULT 1, show_intro INTEGER DEFAULT 1, show_clients INTEGER DEFAULT 1, show_videos INTEGER DEFAULT 1)""")
        cols = [("whatsapp","971500000000"),("phone",""),("email",""),("address",""),("map_url",""),("instagram",""),("facebook",""),
            ("founder_name","Founder Name"),("founder_title","Founder & CEO"),("founder_desc","Passionate about creating beautiful outdoor spaces across Dubai."),
            ("founder_image",""),("services_bg",""),("admin_pass",""),("delete_pass",""),
            ("stat_projects","150"),("stat_years","12"),("stat_satisfaction","98"),("stat_team","25"),("stat_happy","200"),("stat_reviews","180"),("counters_bg",""),("faq_image",""),("faq_heading","Some General Question?"),("cta_bg",""),("form_title","Transform Your Dream Landscape with a Tailored Consultation"),("form_subtitle","Book a private, one-on-one consultation with Dubais leading landscaping experts to explore a bespoke outdoor design tailored to your villa and lifestyle."),("form_heading","Schedule Your Free Consultation"),
            ("smtp_sender",""),("smtp_app_pass",""),("smtp_receiver",""),
            ("intro_title","Green Space Landscaping Services"),
            ("intro_text","We believe outdoor spaces should be sanctuaries that nurture well-being and celebrate nature."),
            ("intro_image",""),("intro_badge","6+"),("intro_badge_label","Year Experience"),
            ("show_services","1"),("show_about","1"),("show_founder","1"),("show_testimonials","1"),("show_faqs","1"),("show_gallery","1"),("show_intro","1"),("show_clients","1"),("show_videos","1"),("favicon","")]
        for col,d in cols:
            try:
                c.execute(f"SELECT {col} FROM settings LIMIT 1")
            except Exception:
                try:
                    de = str(d).replace("'", "''")
                    c.execute(f"ALTER TABLE settings ADD COLUMN {col} TEXT DEFAULT '{de}'")
                except Exception:
                    try: c.execute(f"ALTER TABLE settings ADD COLUMN {col} TEXT DEFAULT ''")
                    except Exception: pass
        # force-add critical columns if missing
        for col in ("cta_bg","form_title","form_subtitle","form_heading","counters_bg","faq_image","faq_heading","stat_team","stat_happy","stat_reviews","show_clients","services_bg","intro_image","show_videos","favicon"):
            try: c.execute(f"SELECT {col} FROM settings LIMIT 1")
            except Exception:
                try: c.execute(f"ALTER TABLE settings ADD COLUMN {col} TEXT DEFAULT ''")
                except Exception: pass
        for sql in [
            "CREATE TABLE IF NOT EXISTS services (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, short_desc TEXT, full_desc TEXT, image TEXT DEFAULT '')",
            "CREATE TABLE IF NOT EXISTS service_images (id INTEGER PRIMARY KEY AUTOINCREMENT, service_id INTEGER, filename TEXT)",
            "CREATE TABLE IF NOT EXISTS hero_images (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT)",
            "CREATE TABLE IF NOT EXISTS gallery (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, caption TEXT DEFAULT '')",
            "CREATE TABLE IF NOT EXISTS testimonials (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, role TEXT DEFAULT '', content TEXT, rating INTEGER DEFAULT 5)",
            "CREATE TABLE IF NOT EXISTS faqs (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, answer TEXT)",
            "CREATE TABLE IF NOT EXISTS external_links (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, url TEXT)",
            "CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT DEFAULT '', logo TEXT)",
            "CREATE TABLE IF NOT EXISTS work_videos (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, caption TEXT DEFAULT '')"]:
            c.execute(sql)
        if not c.execute("SELECT 1 FROM settings").fetchone():
            c.execute("INSERT INTO settings (id, admin_pass) VALUES (1, ?)", (generate_password_hash("admin123"),))
        else:
            row = c.execute("SELECT admin_pass FROM settings WHERE id=1").fetchone()
            if not row["admin_pass"]:
                c.execute("UPDATE settings SET admin_pass=? WHERE id=1", (generate_password_hash("admin123"),))
        if not c.execute("SELECT 1 FROM services").fetchone():
            c.executemany("INSERT INTO services (title,short_desc,full_desc) VALUES (?,?,?)",[
                ("Landscape Design and Build","Custom landscaping that blends beauty and function.","Full design-and-build."),
                ("Landscape Lighting","Expert lighting for safety and ambience.","Layered lighting."),
                ("Water Features","Fountains, ponds and waterfalls.","Custom water features.")])
        if not c.execute("SELECT 1 FROM faqs").fetchone():
            c.executemany("INSERT INTO faqs (question,answer) VALUES (?,?)",[
                ("How long does a project take?","Most projects take 4–12 weeks."),
                ("Do you handle permits?","Yes, we manage Dubai approvals."),
                ("What areas do you serve?","All major Dubai communities.")])
        if not c.execute("SELECT 1 FROM testimonials").fetchone():
            c.execute("INSERT INTO testimonials (name,role,content,rating) VALUES (?,?,?,?)",
                      ("Ahmed Al Maktoum","Villa Owner, Dubai Hills","TECHSERENIA transformed our outdoor space.",5))

init_db()


def ensure_settings_cols():
    need = ["cta_bg","form_title","form_subtitle","form_heading","counters_bg","faq_image","faq_heading","stat_team","stat_happy","stat_reviews","show_clients","services_bg","intro_image","intro_title","intro_text","intro_badge","intro_badge_label","show_videos","favicon"]
    with db() as c:
        for col in need:
            try: c.execute(f"SELECT {col} FROM settings LIMIT 1")
            except Exception:
                try: c.execute(f"ALTER TABLE settings ADD COLUMN {col} TEXT DEFAULT ''")
                except Exception: pass

def gs():
    with db() as c: return dict(c.execute("SELECT * FROM settings WHERE id=1").fetchone())
def check_admin_pass(pw):
    s=gs(); stored=s.get("admin_pass") or ""
    if not stored: return pw=="admin123"
    try: return check_password_hash(stored, pw)
    except: return pw=="admin123"
def extract_map_src(val):
    if not val: return ""
    m=re.search(r'src=["\']([^"\']+)["\']', val); return m.group(1) if m else val.strip()
def get_hero_images():
    with db() as c:
        rows=[r["filename"] for r in c.execute("SELECT filename FROM hero_images ORDER BY id")]
        if not rows:
            s=gs()
            if s.get("bg_file") and s.get("bg_type")!="video": rows=[s["bg_file"]]
        return rows
def get_services():
    with db() as c:
        svcs=[dict(r) for r in c.execute("SELECT * FROM services ORDER BY id")]
        for s in svcs:
            imgs=c.execute("SELECT filename FROM service_images WHERE service_id=?",(s["id"],)).fetchall()
            s["images"]=[i["filename"] for i in imgs] or ([s["image"]] if s.get("image") else [])
        return svcs
def get_service(sid):
    with db() as c:
        r=c.execute("SELECT * FROM services WHERE id=?",(sid,)).fetchone()
        if not r: return None
        s=dict(r); s["images"]=[dict(i) for i in c.execute("SELECT id,filename FROM service_images WHERE service_id=?",(sid,))]; return s
def get_gallery():
    with db() as c: return [dict(r) for r in c.execute("SELECT * FROM gallery ORDER BY id DESC")]
def get_testimonials():
    with db() as c: return [dict(r) for r in c.execute("SELECT * FROM testimonials ORDER BY id DESC")]
def get_faqs():
    with db() as c: return [dict(r) for r in c.execute("SELECT * FROM faqs ORDER BY id")]
def get_links():
    with db() as c: return [dict(r) for r in c.execute("SELECT * FROM external_links ORDER BY id")]
def get_clients():
    with db() as c: return [dict(r) for r in c.execute("SELECT * FROM clients ORDER BY id")]
def get_videos():
    with db() as c: return [dict(r) for r in c.execute("SELECT * FROM work_videos ORDER BY id DESC")]
def all_images():
    imgs=[]
    with db() as c:
        for r in c.execute("SELECT id,filename FROM hero_images"): imgs.append({"type":"hero","id":r["id"],"filename":r["filename"]})
        for r in c.execute("SELECT id,filename FROM service_images"): imgs.append({"type":"service","id":r["id"],"filename":r["filename"]})
        for r in c.execute("SELECT id,filename FROM gallery"): imgs.append({"type":"gallery","id":r["id"],"filename":r["filename"]})
        for r in c.execute("SELECT id,logo as filename FROM clients WHERE logo!=''"): imgs.append({"type":"client","id":r["id"],"filename":r["filename"]})
        s=gs()
        for t,k in [("logo","logo"),("founder","founder_image"),("services_bg","services_bg"),("intro","intro_image"),("counters_bg","counters_bg"),("faq","faq_image"),("cta","cta_bg")]:
            if s.get(k): imgs.append({"type":t,"id":0,"filename":s[k]})
    return imgs

def send_quote_email(name, phone, email, location, message):
    s=gs(); sender,app_pass,receiver=s.get("smtp_sender",""),s.get("smtp_app_pass",""),s.get("smtp_receiver","")
    if not sender or not app_pass or not receiver: return False,"Email not configured"
    body=f"New Quote Request\n\nName: {name}\nPhone: {phone}\nEmail: {email}\nLocation: {location}\n\nMessage:\n{message}"
    msg=MIMEMultipart(); msg["From"]=sender; msg["To"]=receiver; msg["Subject"]=f"Quote Request from {name}"
    msg.attach(MIMEText(body,"plain"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com",465,timeout=15) as server:
            server.login(sender, app_pass); server.sendmail(sender, receiver, msg.as_string())
        return True,"Sent"
    except Exception as e: return False,str(e)

@app.route("/")
def index():
    return render_template("index.html", s=gs(), services=get_services(), testimonials=get_testimonials(),
        faqs=get_faqs(), links=get_links(), hero_images=get_hero_images(), gallery=get_gallery(), clients=get_clients(), videos=get_videos())

@app.route("/services/<int:sid>")
def service_detail(sid):
    svc=get_service(sid)
    if not svc: return redirect(url_for("index")+"#services")
    return render_template("service_detail.html", s=gs(), service=svc, links=get_links())

@app.route("/terms")
def terms():
    return render_template("legal.html", s=gs(), links=get_links(), title="Terms of Service", content="By using TECHSERENIA services you agree to our terms.")
@app.route("/privacy")
def privacy():
    return render_template("legal.html", s=gs(), links=get_links(), title="Privacy Policy", content="We collect only information needed to provide our services.")

@app.route("/api/quote", methods=["POST"])
def api_quote():
    data=request.get_json(silent=True) or request.form
    name=data.get("name","").strip(); phone=data.get("phone","").strip()
    email=data.get("email","").strip(); location=data.get("location","").strip(); message=data.get("message","").strip()
    if not name or not phone: return jsonify({"ok":False,"error":"Name and phone required"}),400
    ok,err=send_quote_email(name,phone,email,location,message)
    return jsonify({"ok":True}) if ok else (jsonify({"ok":False,"error":err}),500)

@app.route("/manifest.json")
def manifest(): return send_file("static/manifest.json", mimetype="application/manifest+json")
@app.route("/sw.js")
def sw(): return send_file("static/sw.js", mimetype="application/javascript")
@app.route("/favicon.ico")
def favicon():
    s=gs(); fav=s.get("favicon") or ""
    path=os.path.join(UPLOAD, fav) if fav and os.path.exists(os.path.join(UPLOAD, fav)) else None
    if not path:
        path=os.path.join(UPLOAD, "icon-192.png") if os.path.exists(os.path.join(UPLOAD, "icon-192.png")) else None
    if not path: return ("", 204)
    ext=path.rsplit(".",1)[-1].lower()
    mime="image/x-icon" if ext=="ico" else ("image/png" if ext=="png" else "image/"+ext)
    return send_file(path, mimetype=mime)

@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method=="POST" and "password" in request.form and not session.get("admin"):
        if check_admin_pass(request.form.get("password","")):
            session["admin"]=True; return redirect(url_for("admin"))
        flash("Wrong password")
    if not session.get("admin"):
        return render_template("admin.html", login=True, s=gs(), services=[], testimonials=[], faqs=[], links=[], hero_images=[], gallery=[], clients=[], all_imgs=[], videos=[])

    if request.method=="POST":
        act=request.form.get("action")
        if act=="save_settings":
            ensure_settings_cols()
            keys=["company_name","hero_title","hero_subtitle","bg_type","whatsapp","phone","email","address","map_url","instagram","facebook",
                  "founder_name","founder_title","founder_desc","stat_projects","stat_years","stat_satisfaction","stat_team","stat_happy","stat_reviews","faq_heading","form_title","form_subtitle","form_heading",
                  "smtp_sender","smtp_app_pass","smtp_receiver","intro_title","intro_text","intro_badge","intro_badge_label"]
            d={k:request.form.get(k,"").strip() for k in keys}
            d["company_name"]=d["company_name"] or "TECHSERENIA"
            d["whatsapp"]=d["whatsapp"].replace("+","").replace(" ","").replace("-","")
            d["map_url"]=extract_map_src(d["map_url"])
            if not d["smtp_app_pass"]: d["smtp_app_pass"]=gs().get("smtp_app_pass") or ""
            vis_keys=["show_services","show_about","show_founder","show_testimonials","show_faqs","show_gallery","show_intro","show_clients","show_videos"]
            vis={k:1 if request.form.get(k) in ("1","on") else 0 for k in vis_keys}
            if not request.form.get("visibility_form"):
                s0=gs()
                for k in vis: vis[k]=int(s0.get(k) or 1)
            logo,bg,fi,sbg,ii,cbg,fiq,cta,fav=gs().get("logo",""),gs().get("bg_file",""),gs().get("founder_image",""),gs().get("services_bg",""),gs().get("intro_image",""),gs().get("counters_bg",""),gs().get("faq_image",""),gs().get("cta_bg",""),gs().get("favicon","")
            for field,var in [("logo","logo"),("bg_file","bg"),("founder_image","fi"),("services_bg","sbg"),("intro_image","ii"),("counters_bg","cbg"),("faq_image","fiq"),("cta_bg","cta"),("favicon","fav")]:
                if field in request.files and request.files[field].filename:
                    f=request.files[field]
                    if f.filename.rsplit(".",1)[-1].lower() in ALLOWED:
                        fname=secure_filename(f.filename); f.save(os.path.join(UPLOAD,fname))
                        if field=="logo": logo=fname
                        elif field=="bg_file": bg=fname
                        elif field=="founder_image": fi=fname
                        elif field=="services_bg": sbg=fname
                        elif field=="intro_image": ii=fname
                        elif field=="counters_bg": cbg=fname
                        elif field=="faq_image": fiq=fname
                        elif field=="cta_bg": cta=fname
                        elif field=="favicon": fav=fname
                        else: pass
            with db() as c:
                c.execute("""UPDATE settings SET company_name=?,hero_title=?,hero_subtitle=?,logo=?,bg_type=?,bg_file=?,favicon=?,
                    whatsapp=?,phone=?,email=?,address=?,map_url=?,instagram=?,facebook=?,
                    founder_name=?,founder_title=?,founder_desc=?,founder_image=?,services_bg=?,
                    stat_projects=?,stat_years=?,stat_satisfaction=?,stat_team=?,stat_happy=?,stat_reviews=?,counters_bg=?,faq_image=?,faq_heading=?,cta_bg=?,form_title=?,form_subtitle=?,form_heading=?,
                    smtp_sender=?,smtp_app_pass=?,smtp_receiver=?,
                    intro_title=?,intro_text=?,intro_image=?,intro_badge=?,intro_badge_label=?,
                    show_services=?,show_about=?,show_founder=?,show_testimonials=?,show_faqs=?,show_gallery=?,show_intro=?,show_clients=?,show_videos=? WHERE id=1""",
                    (d["company_name"],d["hero_title"],d["hero_subtitle"],logo,d["bg_type"],bg,fav,
                     d["whatsapp"],d["phone"],d["email"],d["address"],d["map_url"],d["instagram"],d["facebook"],
                     d["founder_name"],d["founder_title"],d["founder_desc"],fi,sbg,
                     d["stat_projects"],d["stat_years"],d["stat_satisfaction"],d["stat_team"],d["stat_happy"],d["stat_reviews"],cbg,fiq,d.get("faq_heading",""),cta,d.get("form_title",""),d.get("form_subtitle",""),d.get("form_heading",""),
                     d["smtp_sender"],d["smtp_app_pass"],d["smtp_receiver"],
                     d["intro_title"],d["intro_text"],ii,d["intro_badge"],d["intro_badge_label"],
                     vis["show_services"],vis["show_about"],vis["show_founder"],vis["show_testimonials"],vis["show_faqs"],vis["show_gallery"],vis["show_intro"],vis["show_clients"],vis["show_videos"]))
            flash("Saved")
        elif act=="add_hero_images":
            with db() as c:
                for f in request.files.getlist("hero_images"):
                    if f and f.filename and f.filename.rsplit(".",1)[-1].lower() in ALLOWED:
                        fname=secure_filename(f.filename); f.save(os.path.join(UPLOAD,fname))
                        c.execute("INSERT INTO hero_images (filename) VALUES (?)",(fname,))
            flash("Added")
        elif act=="delete_hero_image":
            with db() as c: c.execute("DELETE FROM hero_images WHERE id=?",(request.form.get("id"),)); flash("Deleted")
        elif act=="add_gallery":
            with db() as c:
                for f in request.files.getlist("gallery_images"):
                    if f and f.filename and f.filename.rsplit(".",1)[-1].lower() in ALLOWED:
                        fname=secure_filename(f.filename); f.save(os.path.join(UPLOAD,fname))
                        c.execute("INSERT INTO gallery (filename,caption) VALUES (?,?)",(fname,request.form.get("caption","")))
            flash("Gallery photos added")
        elif act=="delete_gallery":
            with db() as c: c.execute("DELETE FROM gallery WHERE id=?",(request.form.get("id"),)); flash("Deleted")
        elif act=="add_video":
            with db() as c:
                for f in request.files.getlist("work_videos"):
                    if f and f.filename and f.filename.rsplit(".",1)[-1].lower() in ("mp4","webm","mov"):
                        fname=secure_filename(f.filename); f.save(os.path.join(UPLOAD,fname))
                        c.execute("INSERT INTO work_videos (filename,caption) VALUES (?,?)",(fname,request.form.get("caption","")))
            flash("Videos added")
        elif act=="delete_video":
            with db() as c: c.execute("DELETE FROM work_videos WHERE id=?",(request.form.get("id"),)); flash("Deleted")
        elif act=="delete_image":
            t,iid=request.form.get("itype"),request.form.get("id")
            with db() as c:
                if t=="hero": c.execute("DELETE FROM hero_images WHERE id=?",(iid,))
                elif t=="service": c.execute("DELETE FROM service_images WHERE id=?",(iid,))
                elif t=="gallery": c.execute("DELETE FROM gallery WHERE id=?",(iid,))
                elif t=="logo": c.execute("UPDATE settings SET logo='' WHERE id=1")
                elif t=="founder": c.execute("UPDATE settings SET founder_image='' WHERE id=1")
                elif t=="services_bg": c.execute("UPDATE settings SET services_bg='' WHERE id=1")
                elif t=="intro": c.execute("UPDATE settings SET intro_image='' WHERE id=1")
                elif t=="counters_bg": c.execute("UPDATE settings SET counters_bg='' WHERE id=1")
                elif t=="faq": c.execute("UPDATE settings SET faq_image='' WHERE id=1")
                elif t=="cta": c.execute("UPDATE settings SET cta_bg='' WHERE id=1")
                elif t=="client": c.execute("DELETE FROM clients WHERE id=?",(iid,))
            flash("Deleted")
        elif act=="add_service":
            title=request.form.get("title","").strip()
            if title:
                with db() as c:
                    cur=c.execute("INSERT INTO services (title,short_desc,full_desc) VALUES (?,?,?)",
                                  (title,request.form.get("short_desc",""),request.form.get("full_desc","")))
                    sid=cur.lastrowid
                    for f in request.files.getlist("images"):
                        if f and f.filename and f.filename.rsplit(".",1)[-1].lower() in ALLOWED:
                            fname=secure_filename(f.filename); f.save(os.path.join(UPLOAD,fname))
                            c.execute("INSERT INTO service_images (service_id,filename) VALUES (?,?)",(sid,fname))
                flash("Added")
        elif act=="add_service_images":
            sid=request.form.get("service_id")
            with db() as c:
                for f in request.files.getlist("images"):
                    if f and f.filename and f.filename.rsplit(".",1)[-1].lower() in ALLOWED:
                        fname=secure_filename(f.filename); f.save(os.path.join(UPLOAD,fname))
                        c.execute("INSERT INTO service_images (service_id,filename) VALUES (?,?)",(sid,fname))
            flash("Added")
        elif act=="delete_service":
            with db() as c:
                c.execute("DELETE FROM service_images WHERE service_id=?",(request.form.get("id"),))
                c.execute("DELETE FROM services WHERE id=?",(request.form.get("id"),)); flash("Deleted")
        elif act=="add_testimonial":
            name=request.form.get("name","").strip(); content=request.form.get("content","").strip()
            role=request.form.get("role","").strip()
            try: rating=int(request.form.get("rating") or 5)
            except: rating=5
            if name and content:
                with db() as c:
                    c.execute("INSERT INTO testimonials (name,role,content,rating) VALUES (?,?,?,?)",(name,role,content,rating))
                flash("Testimonial added")
            else:
                flash("Name and content required")
        elif act=="delete_testimonial":
            with db() as c: c.execute("DELETE FROM testimonials WHERE id=?",(request.form.get("id"),)); flash("Deleted")
        elif act=="add_faq":
            q=request.form.get("question","").strip(); a=request.form.get("answer","").strip()
            if q and a:
                with db() as c: c.execute("INSERT INTO faqs (question,answer) VALUES (?,?)",(q,a)); flash("Added")
        elif act=="delete_faq":
            with db() as c: c.execute("DELETE FROM faqs WHERE id=?",(request.form.get("id"),)); flash("Deleted")
        elif act=="add_client":
            name=request.form.get("name","").strip()
            logo=""
            if "logo" in request.files and request.files["logo"].filename:
                f=request.files["logo"]
                if f.filename.rsplit(".",1)[-1].lower() in ALLOWED:
                    logo=secure_filename(f.filename); f.save(os.path.join(UPLOAD,logo))
            if logo or name:
                with db() as c: c.execute("INSERT INTO clients (name,logo) VALUES (?,?)",(name,logo)); flash("Client added")
        elif act=="delete_client":
            with db() as c: c.execute("DELETE FROM clients WHERE id=?",(request.form.get("id"),)); flash("Deleted")
        elif act=="add_link":
            t=request.form.get("title","").strip(); u=request.form.get("url","").strip()
            if t and u:
                with db() as c: c.execute("INSERT INTO external_links (title,url) VALUES (?,?)",(t,u)); flash("Added")
        elif act=="delete_link":
            with db() as c: c.execute("DELETE FROM external_links WHERE id=?",(request.form.get("id"),)); flash("Deleted")
        elif act=="change_admin_pass":
            cur,new,conf=request.form.get("current",""),request.form.get("new_pass",""),request.form.get("confirm","")
            if not check_admin_pass(cur): flash("Wrong current password")
            elif new!=conf or len(new)<4: flash("Passwords must match (min 4)")
            else:
                with db() as c: c.execute("UPDATE settings SET admin_pass=? WHERE id=1",(generate_password_hash(new),)); flash("Changed")
        elif act=="set_delete_pass":
            if not check_admin_pass(request.form.get("current","")): flash("Wrong admin password")
            else:
                dp=request.form.get("delete_pass","")
                with db() as c: c.execute("UPDATE settings SET delete_pass=? WHERE id=1",(generate_password_hash(dp) if dp else "",)); flash("Set")
        elif act=="backup_db":
            return send_file(DB_PATH, as_attachment=True, download_name="techserenia_backup.db")
        elif act=="restore_db":
            f=request.files.get("dbfile")
            if f and f.filename.endswith(".db"): f.save(DB_PATH); flash("Restored")
            else: flash("Invalid")
        elif act=="delete_db":
            dp=request.form.get("delete_pass",""); s=gs(); ok=False
            if s.get("delete_pass"):
                try: ok=check_password_hash(s["delete_pass"], dp)
                except: ok=False
            else: ok=check_admin_pass(dp)
            if ok:
                if os.path.exists(DB_PATH): os.remove(DB_PATH)
                init_db(); session.clear(); return redirect(url_for("admin"))
            flash("Wrong password")
        return redirect(url_for("admin"))

    with db() as c:
        hero_imgs=[dict(r) for r in c.execute("SELECT id,filename FROM hero_images ORDER BY id")]
    return render_template("admin.html", login=False, s=gs(), services=get_services(),
        testimonials=get_testimonials(), faqs=get_faqs(), links=get_links(),
        hero_images=hero_imgs, gallery=get_gallery(), clients=get_clients(), all_imgs=all_images(), videos=get_videos())

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("index"))

if __name__=="__main__":
    app.run(debug=True, port=5000)
