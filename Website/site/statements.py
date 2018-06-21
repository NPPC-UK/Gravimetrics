get_staff_sql = "select is_phen_staff from user_privileges inner join user_registrations on user_privileges.id_user=user_registrations.id_user where user_registrations.email='{0}'"

get_salt_sql = "select salt from user_registrations where email='{0}'"

get_name_passwd_sql = "select username from user_registrations where email='{0}' and password ='{1}'"
