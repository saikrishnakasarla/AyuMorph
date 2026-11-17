"""
Management command to populate standard reference Ayurvedic plant profiles
for demonstration and initial catalog setup.
"""

from django.core.management.base import BaseCommand
from plants.models import Plant

SEED_PLANTS = [
    {
        "name": "Tulsi (Holy Basil)",
        "scientific_name": "Ocimum tenuiflorum",
        "category": "Ayurvedic Plant",
        "description": "An aromatic perennial plant in the family Lamiaceae, native to the Indian subcontinent and widespread throughout Southeast Asia.",
        "morphology": "Erect, much-branched subshrub, 30-60 cm tall with hairy stems. Leaves are green or purple, ovate, up to 5 cm long, usually slightly toothed margin, strongly scented.",
        "identification_features": "Opposite decussate leaves, square cross-section stems, glandular hairs emitting a pungent clove-like fragrance, purplish-pink floral whorls.",
        "traditional_uses": "Commonly documented in Ayurvedic texts as an adaptogen and rasayana. Traditionally used in herbal infusions for seasonal respiratory comfort, vitality, and digestive support."
    },
    {
        "name": "Neem",
        "scientific_name": "Azadirachta indica",
        "category": "Ayurvedic Plant",
        "description": "A tree in the mahogany family Meliaceae, native to the Indian subcontinent and widely cultivated in tropical and subtropical regions.",
        "morphology": "Medium to large evergreen tree, reaching 15-20 m height. Compound imparipinnate leaves with 20-30 leaflets. Small, white, fragrant bisexual and staminate flowers.",
        "identification_features": "Alternate pinnate leaves with asymmetrical serrated leaflets, bitter taste throughout all vegetative parts, smooth greenish-white bark when young turning fissured grey.",
        "traditional_uses": "Traditional Ayurvedic applications document the use of bark, leaves, and seed oil for external skin cleansing, dental hygiene twigs (datun), and as a traditional cooling bitter herb."
    },
    {
        "name": "Ashwagandha",
        "scientific_name": "Withania somnifera",
        "category": "Ayurvedic Plant",
        "description": "A small woody shrub in the Solanaceae (nightshade) family, recognized historically across classical Ayurvedic literature.",
        "morphology": "Short, tender perennial shrub growing 35-75 cm tall. Tomentose branches extending radially from a central stem. Small, green, bell-shaped flowers and bright orange-red berries enclosed in a papery calyx.",
        "identification_features": "Dull green elliptic leaves with stellate hairs, fleshy brownish roots with characteristic earthy aroma, persistent papery calyx surrounding mature red berry.",
        "traditional_uses": "Documented in classical texts as a Medhya Rasayana. Traditionally prepared with warm milk or honey for physical stamina, calm sleep, and stress balance."
    },
    {
        "name": "Brahmi",
        "scientific_name": "Bacopa monnieri",
        "category": "Ayurvedic Plant",
        "description": "A non-aromatic creeping perennial herb native to the wetlands of southern and eastern India, Australia, and the Americas.",
        "morphology": "Succulent, creeping herb with rooting at the nodes. Leaves are oblanceolate, 4-6 mm thick, arranged oppositely on the stem. Small, white or pale violet actinomorphic flowers with 4-5 petals.",
        "identification_features": "Oblong to spatulate succulent leaves, prostrate growth habit in moist soil, solitary axillary pale blue or white flowers.",
        "traditional_uses": "Historically recorded in Charaka Samhita as a cognitive enhancer. Traditional applications include preparing medicated ghee (Ghrita) for memory retention and mental clarity."
    },
    {
        "name": "Amla (Indian Gooseberry)",
        "scientific_name": "Phyllanthus emblica",
        "category": "Ayurvedic Plant",
        "description": "A deciduous tree of the family Phyllanthaceae, celebrated for its edible, nutrient-dense spherical fruits.",
        "morphology": "Small to medium deciduous tree reaching 8-18 m. Branchlets light green with simple, closely set, pinnately arranged small oblong leaves resembling compound leaves.",
        "identification_features": "Feathery foliage with tiny oblong distichous leaves, smooth grey-green peeling bark, hard spherical greenish-yellow fruits with 6 vertical furrows.",
        "traditional_uses": "The primary ingredient in traditional Chyawanprash. Documented in Ayurvedic compendia as a Pitta-pacifying rasayana, utilized traditionally for digestive balance and rejuvenation."
    },
    {
        "name": "Aloe Vera (Ghritkumari)",
        "scientific_name": "Aloe barbadensis miller",
        "category": "Medicinal Herb",
        "description": "A stemless or very short-stemmed succulent plant species belonging to the genus Aloe.",
        "morphology": "Thick, fleshy, lanceolate leaves arranged in a rosette. Leaves are green to grey-green, with serrated margins bearing small white teeth. Yellow tubular flowers on tall racemes.",
        "identification_features": "Rosette arrangement of mucilaginous, fleshy leaves with marginal spines; clear inner parenchymal gel surrounded by bitter yellow aloin latex.",
        "traditional_uses": "Documented traditionally for topical application to soothe skin irritations and minor burns, as well as oral preparations for soothing the gastrointestinal tract."
    }
]

class Command(BaseCommand):
    help = 'Seeds initial reference botanical records into the database'

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for item in SEED_PLANTS:
            plant, created = Plant.objects.update_or_create(
                scientific_name=item["scientific_name"],
                defaults={
                    "name": item["name"],
                    "category": item["category"],
                    "description": item["description"],
                    "morphology": item["morphology"],
                    "identification_features": item["identification_features"],
                    "traditional_uses": item["traditional_uses"],
                    "is_active": True,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"+ Created: {plant.name}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.NOTICE(f"= Updated: {plant.name}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded database: {created_count} created, {updated_count} existing verified."
            )
        )
