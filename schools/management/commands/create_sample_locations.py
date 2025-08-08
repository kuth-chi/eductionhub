from django.core.management.base import BaseCommand
from geo.models import Country, State, City, Village


class Command(BaseCommand):
    help = "Create sample location data (countries, states, cities, villages)"

    def handle(self, *args, **options):
        self.stdout.write("Creating sample location data...")

        # Create Countries
        cambodia = Country.objects.create(
            name="Cambodia", code="KHM", phone_code="+855", flag_emoji="🇰🇭"
        )

        thailand = Country.objects.create(
            name="Thailand", code="THA", phone_code="+66", flag_emoji="🇹🇭"
        )

        vietnam = Country.objects.create(
            name="Vietnam", code="VNM", phone_code="+84", flag_emoji="🇻🇳"
        )

        # Create States for Cambodia
        phnom_penh_state = State.objects.create(
            name="Phnom Penh", code="PP", country=cambodia
        )

        siem_reap_state = State.objects.create(
            name="Siem Reap", code="SR", country=cambodia
        )

        battambang_state = State.objects.create(
            name="Battambang", code="BTB", country=cambodia
        )

        # Create States for Thailand
        bangkok_state = State.objects.create(
            name="Bangkok", code="BKK", country=thailand
        )

        chiang_mai_state = State.objects.create(
            name="Chiang Mai", code="CM", country=thailand
        )

        # Create States for Vietnam
        ho_chi_minh_state = State.objects.create(
            name="Ho Chi Minh City", code="HCM", country=vietnam
        )

        hanoi_state = State.objects.create(name="Hanoi", code="HN", country=vietnam)

        # Create Cities for Cambodia
        phnom_penh_city = City.objects.create(
            name="Phnom Penh", code="PP", state=phnom_penh_state, is_capital=True
        )

        siem_reap_city = City.objects.create(
            name="Siem Reap", code="SR", state=siem_reap_state, is_capital=True
        )

        battambang_city = City.objects.create(
            name="Battambang", code="BTB", state=battambang_state, is_capital=True
        )

        # Create Cities for Thailand
        bangkok_city = City.objects.create(
            name="Bangkok", code="BKK", state=bangkok_state, is_capital=True
        )

        chiang_mai_city = City.objects.create(
            name="Chiang Mai", code="CM", state=chiang_mai_state, is_capital=True
        )

        # Create Cities for Vietnam
        ho_chi_minh_city = City.objects.create(
            name="Ho Chi Minh City",
            code="HCM",
            state=ho_chi_minh_state,
            is_capital=True,
        )

        hanoi_city = City.objects.create(
            name="Hanoi", code="HN", state=hanoi_state, is_capital=True
        )

        # Create Villages for Cambodia
        Village.objects.create(name="Chamkar Mon", code="CM", city=phnom_penh_city)

        Village.objects.create(name="Daun Penh", code="DP", city=phnom_penh_city)

        Village.objects.create(name="Prampi Makara", code="PM", city=phnom_penh_city)

        Village.objects.create(name="Siem Reap Town", code="SRT", city=siem_reap_city)

        Village.objects.create(name="Battambang Town", code="BTT", city=battambang_city)

        # Create Villages for Thailand
        Village.objects.create(name="Sukhumvit", code="SKV", city=bangkok_city)

        Village.objects.create(name="Silom", code="SLM", city=bangkok_city)

        Village.objects.create(
            name="Chiang Mai Old City", code="CMOC", city=chiang_mai_city
        )

        # Create Villages for Vietnam
        Village.objects.create(name="District 1", code="D1", city=ho_chi_minh_city)

        Village.objects.create(name="District 3", code="D3", city=ho_chi_minh_city)

        Village.objects.create(name="Hoan Kiem", code="HK", city=hanoi_city)

        Village.objects.create(name="Ba Dinh", code="BD", city=hanoi_city)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created location data:\n"
                f"- {Country.objects.count()} Countries\n"
                f"- {State.objects.count()} States\n"
                f"- {City.objects.count()} Cities\n"
                f"- {Village.objects.count()} Villages"
            )
        )
