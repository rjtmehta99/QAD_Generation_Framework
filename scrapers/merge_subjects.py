import helper
import constants

# Merge CSV with subject content and save new CSV
df_chemistry = helper.merge_by_subject(constants.CHEMISTRY_FILES)
df_chemistry.to_csv('data/chemistry_merged.csv', index=False)

df_physics = helper.merge_by_subject(constants.PHYSICS_FILES)
df_physics.to_csv('data/physics_merged.csv', index=False)

df_biology = helper.merge_by_subject(constants.BIOLOGY_FILES)
df_biology.to_csv('data/biology_merged.csv', index=False)

df_econ = helper.merge_by_subject(constants.ECONOMICS_FILES)
df_econ.to_csv('data/economics_merged.csv', index=False)

df_phy_sci = helper.merge_by_subject(constants.PHYSICAL_SCIENCE_FILES)
df_phy_sci.to_csv('data/physical_sciences_merged.csv', index=False)
