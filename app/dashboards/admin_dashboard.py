# app/dashboards/admin_dashboard.py
import streamlit as st
import pandas as pd
from app.database.db_manager import DBManager
from app.components.cards import metric_card
from app.utils.helpers import hash_password
from app.utils.validators import validate_email, validate_username

def render_admin_dashboard(db: DBManager):
    st.title("🛡️ Administrator Portal")
    st.markdown("System Administration, User Roles, and Master Directory Management")

    classes = db.get_all_classes()
    class_map = {f"{c['class_name']} - Div {c['division']}": c["class_id"] for c in classes}

    tab1, tab2, tab3 = st.tabs(["👥 Teacher Management", "🎓 Student Management", "⚙️ System Overview"])

    # ---------------- TAB 1: TEACHER MANAGEMENT ----------------
    with tab1:
        st.subheader("Manage Faculty & Teachers")
        col_t1, col_t2 = st.columns([1, 1])

        with col_t1:
            with st.expander("➕ Add New Teacher", expanded=False):
                with st.form("add_teacher_form"):
                    t_username = st.text_input("Username (for login)")
                    t_password = st.text_input("Temporary Password", type="password")
                    t_name = st.text_input("Full Name (e.g. Prof. Rajesh Sharma)")
                    t_dept = st.text_input("Department (e.g. Computer Science)")
                    t_email = st.text_input("Email Address")

                    st.markdown("**Initial Subject Assignment (Optional):**")
                    opt_sub_code = st.text_input("Subject Code (optional, e.g. CS803)", placeholder="e.g. CS803")
                    opt_sub_name = st.text_input("Subject Name (optional, e.g. Data Analytics)", placeholder="e.g. Data Analytics")
                    opt_sub_class = st.selectbox("Assign to Class", list(class_map.keys()) if class_map else ["None"], key="init_sub_class")

                    t_submit = st.form_submit_button("Create Teacher Account", type="primary")

                    if t_submit:
                        if not (t_username and t_password and t_name and t_dept and t_email):
                            st.error("All basic teacher fields are required.")
                        elif not validate_username(t_username):
                            st.error("Username must be at least 3 alphanumeric characters.")
                        elif not validate_email(t_email):
                            st.error("Please enter a valid email address.")
                        elif db.get_user_by_username(t_username.strip()):
                            st.error(f"Username '{t_username}' is already in use.")
                        else:
                            try:
                                pw_hash = hash_password(t_password)
                                uid = db.create_user(t_username.strip(), pw_hash, "teacher")
                                tid = db.create_teacher(uid, t_name.strip(), t_dept.strip(), t_email.strip())

                                # If initial subject provided
                                if opt_sub_code.strip() and opt_sub_name.strip() and class_map:
                                    cid = class_map[opt_sub_class]
                                    db.create_subject(opt_sub_code.strip().upper(), opt_sub_name.strip(), cid, tid)
                                    st.success(f"Teacher '{t_name}' created and assigned to '{opt_sub_name}'!")
                                else:
                                    st.success(f"Teacher account for '{t_name}' created successfully! Now assign subjects below.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error creating teacher: {e}")

        # List teachers
        teachers = db.get_all_teachers(include_inactive=True)
        if teachers:
            t_data = []
            for t in teachers:
                assigned_subs = db.get_subjects_by_teacher(t["teacher_id"])
                sub_names = ", ".join([s["subject_code"] for s in assigned_subs]) if assigned_subs else "None"
                t_data.append({
                    "Teacher ID": t["teacher_id"],
                    "Name": t["name"],
                    "Username": t["username"],
                    "Department": t["department"],
                    "Email": t["email"],
                    "Assigned Subjects": sub_names,
                    "Status": "Active" if t["is_active"] == 1 else "Deactivated"
                })
            st.dataframe(pd.DataFrame(t_data), use_container_width=True)

            # Action selector
            st.markdown("#### Teacher Actions")
            t_options = {f"{t['name']} ({t['department']}) - ID: {t['teacher_id']}": t for t in teachers}
            selected_t_key = st.selectbox("Select Teacher to Edit / Assign Subjects", list(t_options.keys()))
            selected_t = t_options[selected_t_key]

            col_act1, col_act2 = st.columns(2)
            with col_act1:
                with st.form("edit_teacher_form"):
                    st.write(f"Edit details for **{selected_t['name']}**")
                    edit_name = st.text_input("Name", value=selected_t["name"])
                    edit_dept = st.text_input("Department", value=selected_t["department"])
                    edit_email = st.text_input("Email", value=selected_t["email"])
                    if st.form_submit_button("Update Teacher Details"):
                        if not validate_email(edit_email):
                            st.error("Invalid email address.")
                        else:
                            db.update_teacher(selected_t["teacher_id"], edit_name.strip(), edit_dept.strip(), edit_email.strip())
                            st.success("Teacher updated successfully!")
                            st.rerun()

            with col_act2:
                st.write("#### Account Status")
                if selected_t["is_active"] == 1:
                    st.warning("Deactivating will prevent this teacher from logging in and opening attendance sessions.")
                    if st.button("🚫 Deactivate Teacher Account", type="primary"):
                        db.set_teacher_active(selected_t["teacher_id"], 0)
                        st.success(f"Teacher {selected_t['name']} deactivated.")
                        st.rerun()
                else:
                    st.info("This teacher account is currently deactivated.")
                    if st.button("✅ Reactivate Teacher Account"):
                        db.set_teacher_active(selected_t["teacher_id"], 1)
                        st.success(f"Teacher {selected_t['name']} reactivated.")
                        st.rerun()

            # ---------------- SUBJECT ASSIGNMENT SECTION ----------------
            st.markdown("---")
            st.markdown(f"### 📚 Subject & Class Assignments for **{selected_t['name']}**")

            t_subjects = db.get_subjects_by_teacher(selected_t["teacher_id"])
            if t_subjects:
                st.write("Currently Assigned Subjects:")
                sub_df = pd.DataFrame([{
                    "Subject Code": s["subject_code"],
                    "Subject Name": s["subject_name"],
                    "Class": f"{s['class_name']} - Div {s['division']}",
                    "Total Marks": s["total_marks"]
                } for s in t_subjects])
                st.dataframe(sub_df, use_container_width=True)
            else:
                st.warning(f"⚠️ **{selected_t['name']}** currently has **no subjects assigned**! Without assigned subjects, this teacher cannot open attendance sessions or enter marks in the Teacher Dashboard.")

            col_sub1, col_sub2 = st.columns(2)
            with col_sub1:
                with st.expander("➕ Assign an Existing Subject to this Teacher", expanded=(len(t_subjects) == 0)):
                    all_subjects = db.get_all_subjects()
                    if not all_subjects:
                        st.info("No subjects found in the database. Please create a new subject using the form on the right.")
                    else:
                        sub_choices = {
                            f"{s['subject_name']} ({s['subject_code']}) - {s['class_name']} Div {s['division']} (Currently: {s['teacher_name']})": s["subject_id"]
                            for s in all_subjects
                        }
                        chosen_sub_key = st.selectbox("Select Subject", list(sub_choices.keys()), key=f"sel_sub_{selected_t['teacher_id']}")
                        chosen_sub_id = sub_choices[chosen_sub_key]

                        if st.button(f"Assign to {selected_t['name']}", type="primary", key=f"btn_assign_{selected_t['teacher_id']}"):
                            db.assign_subject_to_teacher(chosen_sub_id, selected_t["teacher_id"])
                            st.success(f"Subject assigned to {selected_t['name']} successfully!")
                            st.rerun()

            with col_sub2:
                with st.expander("🆕 Create & Assign New Subject to this Teacher", expanded=(len(t_subjects) == 0)):
                    with st.form(f"create_sub_form_{selected_t['teacher_id']}"):
                        new_code = st.text_input("Subject Code (e.g. CS803, IT802)")
                        new_name = st.text_input("Subject Name (e.g. Deep Learning, Data Structures)")
                        new_class = st.selectbox("Assign to Class & Division", list(class_map.keys()) if class_map else ["None"], key=f"sub_class_{selected_t['teacher_id']}")
                        new_marks = st.number_input("Total Max Marks", min_value=10, max_value=500, value=100, step=10, key=f"sub_marks_{selected_t['teacher_id']}")

                        if st.form_submit_button("Create & Assign Subject", type="primary"):
                            if not (new_code and new_name and class_map):
                                st.error("Subject code and name are required.")
                            elif db.get_subject_by_code(new_code):
                                st.error(f"Subject code '{new_code.upper()}' already exists. Please use a unique code or assign the existing subject.")
                            else:
                                cid = class_map[new_class]
                                db.create_subject(new_code.strip().upper(), new_name.strip(), cid, selected_t["teacher_id"], int(new_marks))
                                st.success(f"Subject '{new_name}' created and assigned to {selected_t['name']}!")
                                st.rerun()

    # ---------------- TAB 2: STUDENT MANAGEMENT ----------------
    with tab2:
        st.subheader("Manage Students & Enrollments")

        with st.expander("➕ Add New Student", expanded=False):
            with st.form("add_student_form"):
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    s_username = st.text_input("Login Username (e.g. S005)")
                    s_password = st.text_input("Password", type="password")
                    s_name = st.text_input("Student Full Name")
                with col_s2:
                    s_roll = st.text_input("Roll Number (e.g. CS05)")
                    s_class_sel = st.selectbox("Assign Class & Division", list(class_map.keys()) if class_map else ["None"])
                    s_email = st.text_input("Student Email")

                s_submit = st.form_submit_button("Register Student", type="primary")
                if s_submit:
                    if not (s_username and s_password and s_name and s_roll and s_email and class_map):
                        st.error("All fields are required.")
                    elif not validate_email(s_email):
                        st.error("Invalid email address.")
                    elif db.get_user_by_username(s_username.strip()):
                        st.error("Username already exists.")
                    elif db.get_student_by_roll_number(s_roll.strip()):
                        st.error("Roll number already registered.")
                    else:
                        try:
                            pw_hash = hash_password(s_password)
                            uid = db.create_user(s_username.strip(), pw_hash, "student")
                            cid = class_map[s_class_sel]
                            sid = db.create_student(uid, s_name.strip(), s_roll.strip(), cid, s_email.strip())
                            # Auto assign numeric face label
                            db.register_face_label(sid, sid)
                            st.success(f"Student '{s_name}' registered successfully with ID {sid}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error registering student: {e}")

        # Search and list students
        search_kw = st.text_input("🔍 Search Students (by name, roll number, or email)", placeholder="Type keyword to filter...")
        students = db.search_students(search_kw) if search_kw else db.get_all_students(include_inactive=True)

        if students:
            st.dataframe(pd.DataFrame([{
                "Student ID": s["student_id"],
                "Roll No": s["roll_number"],
                "Name": s["name"],
                "Class": f"{s['class_name']} - {s['division']}",
                "Email": s["email"],
                "Username": s["username"],
                "Status": "Active" if s["is_active"] == 1 else "Deactivated"
            } for s in students]), use_container_width=True)

            s_options = {f"{s['roll_number']} - {s['name']} (ID: {s['student_id']})": s for s in students}
            sel_s_key = st.selectbox("Select Student to Edit / Toggle Status", list(s_options.keys()))
            sel_s = s_options[sel_s_key]

            col_se1, col_se2 = st.columns(2)
            with col_se1:
                with st.form("edit_student_form"):
                    st.write(f"Edit details for **{sel_s['name']}**")
                    ed_name = st.text_input("Full Name", value=sel_s["name"])
                    ed_roll = st.text_input("Roll Number", value=sel_s["roll_number"])
                    ed_email = st.text_input("Email", value=sel_s["email"])
                    cur_class_label = f"{sel_s['class_name']} - Div {sel_s['division']}"
                    default_idx = list(class_map.keys()).index(cur_class_label) if cur_class_label in class_map else 0
                    ed_class = st.selectbox("Class", list(class_map.keys()), index=default_idx)
                    if st.form_submit_button("Update Student Record"):
                        if not validate_email(ed_email):
                            st.error("Invalid email.")
                        else:
                            db.update_student(sel_s["student_id"], ed_name.strip(), ed_roll.strip(), class_map[ed_class], ed_email.strip())
                            st.success("Student updated successfully!")
                            st.rerun()

            with col_se2:
                st.write("#### Account Status")
                if sel_s["is_active"] == 1:
                    st.warning("Deactivating will preserve marks and attendance records, but prevent the student from logging in or marking attendance.")
                    if st.button("🚫 Deactivate Student", type="primary"):
                        db.set_student_active(sel_s["student_id"], 0)
                        st.success(f"Student {sel_s['name']} deactivated.")
                        st.rerun()
                else:
                    st.info("Student account is currently deactivated.")
                    if st.button("✅ Reactivate Student"):
                        db.set_student_active(sel_s["student_id"], 1)
                        st.success(f"Student {sel_s['name']} reactivated.")
                        st.rerun()

    # ---------------- TAB 3: SYSTEM OVERVIEW ----------------
    with tab3:
        st.subheader("System Architecture & Metrics")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            all_t = db.get_all_teachers()
            metric_card("Teachers", str(len(all_t)), "Registered faculty")
        with col_m2:
            all_s = db.get_all_students()
            metric_card("Students", str(len(all_s)), "Enrolled students", "#10B981")
        with col_m3:
            all_c = db.get_all_classes()
            metric_card("Classes", str(len(all_c)), "Active classes", "#6366F1")
        with col_m4:
            all_sub = db.get_all_subjects()
            metric_card("Subjects", str(len(all_sub)), "Curriculum courses", "#F59E0B")

        st.markdown("#### 📚 All Curriculum Subjects Master Directory")
        all_subs = db.get_all_subjects()
        if all_subs:
            st.dataframe(pd.DataFrame([{
                "Subject Code": s["subject_code"],
                "Subject Name": s["subject_name"],
                "Class & Division": f"{s['class_name']} - Div {s['division']}",
                "Assigned Faculty": s["teacher_name"],
                "Max Marks": s["total_marks"]
            } for s in all_subs]), use_container_width=True)

        st.info("System running in local SQLite mode with OpenCV Haar Cascade Face Detection and LBPH Recognition.")
