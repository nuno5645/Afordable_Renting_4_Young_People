from django.core.management.base import BaseCommand
from houses.models import District, County, Parish

class Command(BaseCommand):
    help = 'Populate districts, counties and parishes with hardcoded data'

    def handle(self, *args, **options):
        # Districts data
        districts = [
            'Aveiro', 'Beja', 'Braga', 'Bragança', 'Castelo Branco', 'Coimbra',
            'Évora', 'Faro', 'Guarda', 'Ilha da Madeira', 'Ilha das Flores',
            'Ilha de Porto Santo', 'Ilha de Santa Maria', 'Ilha de São Jorge',
            'Ilha de São Miguel', 'Ilha do Corvo', 'Ilha do Faial', 'Ilha do Pico',
            'Ilha Graciosa', 'Ilha Terceira', 'Leiria', 'Lisboa', 'Portalegre',
            'Porto', 'Santarém', 'Setúbal', 'Viana do Castelo', 'Vila Real', 'Viseu'
        ]

        # Counties data (district_id, county_name)
        counties_data = [
            (1, 'Águeda'), (1, 'Albergaria-a-Velha'), (1, 'Anadia'), (1, 'Arouca'),
            (1, 'Aveiro'), (1, 'Castelo de Paiva'), (1, 'Espinho'), (1, 'Estarreja'),
            (1, 'Ílhavo'), (1, 'Mealhada'), (1, 'Murtosa'), (1, 'Oliveira de Azeméis'),
            (1, 'Oliveira do Bairro'), (1, 'Ovar'), (1, 'Santa Maria da Feira'),
            (1, 'São João da Madeira'), (1, 'Sever do Vouga'), (1, 'Vagos'), (1, 'Vale de Cambra'),
            (2, 'Aljustrel'), (2, 'Almodôvar'), (2, 'Alvito'), (2, 'Barrancos'), (2, 'Beja'),
            (2, 'Castro Verde'), (2, 'Cuba'), (2, 'Ferreira do Alentejo'), (2, 'Mértola'),
            (2, 'Moura'), (2, 'Odemira'), (2, 'Ourique'), (2, 'Serpa'), (2, 'Vidigueira'),
            (3, 'Amares'), (3, 'Barcelos'), (3, 'Braga'), (3, 'Cabeceiras de Basto'),
            (3, 'Celorico de Basto'), (3, 'Esposende'), (3, 'Fafe'), (3, 'Guimarães'),
            (3, 'Póvoa de Lanhoso'), (3, 'Terras de Bouro'), (3, 'Vieira do Minho'),
            (3, 'Vila Nova de Famalicão'), (3, 'Vila Verde'), (3, 'Vizela'),
            (4, 'Alfândega da Fé'), (4, 'Bragança'), (4, 'Carrazeda de Ansiães'),
            (4, 'Freixo de Espada à Cinta'), (4, 'Macedo de Cavaleiros'), (4, 'Miranda do Douro'),
            (4, 'Mirandela'), (4, 'Mogadouro'), (4, 'Torre de Moncorvo'), (4, 'Vila Flor'),
            (4, 'Vimioso'), (4, 'Vinhais'),
            (5, 'Belmonte'), (5, 'Castelo Branco'), (5, 'Covilhã'), (5, 'Fundão'),
            (5, 'Idanha-a-Nova'), (5, 'Oleiros'), (5, 'Penamacor'), (5, 'Proença-a-Nova'),
            (5, 'Sertã'), (5, 'Vila de Rei'), (5, 'Vila Velha de Ródão'),
            (6, 'Arganil'), (6, 'Cantanhede'), (6, 'Coimbra'), (6, 'Condeixa-a-Nova'),
            (6, 'Figueira da Foz'), (6, 'Góis'), (6, 'Lousã'), (6, 'Mira'),
            (6, 'Miranda do Corvo'), (6, 'Montemor-o-Velho'), (6, 'Oliveira do Hospital'),
            (6, 'Pampilhosa da Serra'), (6, 'Penacova'), (6, 'Penela'), (6, 'Soure'),
            (6, 'Tábua'), (6, 'Vila Nova de Poiares'),
            (7, 'Alandroal'), (7, 'Arraiolos'), (7, 'Borba'), (7, 'Estremoz'), (7, 'Évora'),
            (7, 'Montemor-o-Novo'), (7, 'Mora'), (7, 'Mourão'), (7, 'Portel'), (7, 'Redondo'),
            (7, 'Reguengos de Monsaraz'), (7, 'Vendas Novas'), (7, 'Viana do Alentejo'), (7, 'Vila Viçosa'),
            (8, 'Albufeira'), (8, 'Alcoutim'), (8, 'Aljezur'), (8, 'Castro Marim'), (8, 'Faro'),
            (8, 'Lagoa'), (8, 'Lagos'), (8, 'Loulé'), (8, 'Monchique'), (8, 'Olhão'),
            (8, 'Portimão'), (8, 'São Brás de Alportel'), (8, 'Silves'), (8, 'Tavira'),
            (8, 'Vila do Bispo'), (8, 'Vila Real de Santo António'),
            (9, 'Aguiar da Beira'), (9, 'Almeida'), (9, 'Celorico da Beira'),
            (9, 'Figueira de Castelo Rodrigo'), (9, 'Fornos de Algodres'), (9, 'Gouveia'),
            (9, 'Guarda'), (9, 'Manteigas'), (9, 'Mêda'), (9, 'Pinhel'), (9, 'Sabugal'),
            (9, 'Seia'), (9, 'Trancoso'), (9, 'Vila Nova de Foz Côa'),
            (10, 'Calheta'), (10, 'Câmara de Lobos'), (10, 'Funchal'), (10, 'Machico'),
            (10, 'Ponta do Sol'), (10, 'Porto Moniz'), (10, 'Ribeira Brava'), (10, 'Santa Cruz'),
            (10, 'Santana'), (10, 'São Vicente'),
            (11, 'Lajes das Flores'), (11, 'Santa Cruz das Flores'),
            (12, 'Porto Santo'),
            (13, 'Vila do Porto'),
            (14, 'Calheta de São Jorge'), (14, 'Velas'),
            (15, 'Lagoa'), (15, 'Nordeste'), (15, 'Ponta Delgada'), (15, 'Povoação'),
            (15, 'Ribeira Grande'), (15, 'Vila Franca do Campo'),
            (16, 'Corvo'),
            (17, 'Horta'),
            (18, 'Lajes do Pico'), (18, 'Madalena'), (18, 'São Roque do Pico'),
            (19, 'Santa Cruz da Graciosa'),
            (20, 'Angra do Heroísmo'), (20, 'Praia da Vitória'),
            (21, 'Alcobaça'), (21, 'Alvaiázere'), (21, 'Ansião'), (21, 'Batalha'),
            (21, 'Bombarral'), (21, 'Caldas da Rainha'), (21, 'Castanheira de Pêra'),
            (21, 'Figueiró dos Vinhos'), (21, 'Leiria'), (21, 'Marinha Grande'),
            (21, 'Nazaré'), (21, 'Óbidos'), (21, 'Pedrógão Grande'), (21, 'Peniche'),
            (21, 'Pombal'), (21, 'Porto de Mós'),
            (22, 'Alenquer'), (22, 'Amadora'), (22, 'Arruda dos Vinhos'), (22, 'Azambuja'),
            (22, 'Cadaval'), (22, 'Cascais'), (22, 'Lisboa'), (22, 'Loures'),
            (22, 'Lourinhã'), (22, 'Mafra'), (22, 'Odivelas'), (22, 'Oeiras'),
            (22, 'Sintra'), (22, 'Sobral de Monte Agraço'), (22, 'Torres Vedras'),
            (22, 'Vila Franca de Xira'),
            (23, 'Alter do Chão'), (23, 'Arronches'), (23, 'Avis'), (23, 'Campo Maior'),
            (23, 'Castelo de Vide'), (23, 'Crato'), (23, 'Elvas'), (23, 'Fronteira')
        ]

        # Parishes data for Lisboa district (county_name, parish_name)
        parishes_data = [
            # Alenquer
            ('Alenquer', 'Alenquer (Santo Estêvão e Triana)'),
            ('Alenquer', 'Aldeia Galega da Merceana e Aldeia Gavinha'),
            ('Alenquer', 'Cadafais'),
            ('Alenquer', 'Carregado'),
            ('Alenquer', 'Meca'),
            ('Alenquer', 'Ribafria e Pereiro de Palhacana'),
            ('Alenquer', 'Vila Verde dos Francos'),
            
            # Amadora
            ('Amadora', 'Águas Livres'),
            ('Amadora', 'Alfragide'),
            ('Amadora', 'Falagueira-Venda Nova'),
            ('Amadora', 'Mina de Água'),
            ('Amadora', 'Reboleira'),
            ('Amadora', 'Venteira'),
            
            # Arruda dos Vinhos
            ('Arruda dos Vinhos', 'Arruda dos Vinhos'),
            ('Arruda dos Vinhos', 'Cardosas'),
            ('Arruda dos Vinhos', 'Santiago dos Velhos'),
            
            # Azambuja
            ('Azambuja', 'Azambuja'),
            ('Azambuja', 'Aveiras de Baixo'),
            ('Azambuja', 'Aveiras de Cima'),
            ('Azambuja', 'Manique do Intendente, Vila Nova de São Pedro e Maçussa'),
            ('Azambuja', 'Vale do Paraíso'),
            
            # Cadaval
            ('Cadaval', 'Cadaval e Pêro Moniz'),
            ('Cadaval', 'Cercal'),
            ('Cadaval', 'Lamas e Cercal'),
            ('Cadaval', 'Painho e Figueiros'),
            ('Cadaval', 'Vermelha'),
            ('Cadaval', 'Vilar'),
            
            # Cascais
            ('Cascais', 'Alcabideche'),
            ('Cascais', 'Carcavelos e Parede'),
            ('Cascais', 'Cascais e Estoril'),
            ('Cascais', 'São Domingos de Rana'),
            
            # Lisboa
            ('Lisboa', 'Ajuda'),
            ('Lisboa', 'Alcântara'),
            ('Lisboa', 'Alvalade'),
            ('Lisboa', 'Areeiro'),
            ('Lisboa', 'Arroios'),
            ('Lisboa', 'Avenidas Novas'),
            ('Lisboa', 'Beato'),
            ('Lisboa', 'Belém'),
            ('Lisboa', 'Benfica'),
            ('Lisboa', 'Campo de Ourique'),
            ('Lisboa', 'Campolide'),
            ('Lisboa', 'Carnide'),
            ('Lisboa', 'Estrela'),
            ('Lisboa', 'Lumiar'),
            ('Lisboa', 'Marvila'),
            ('Lisboa', 'Misericórdia'),
            ('Lisboa', 'Olivais'),
            ('Lisboa', 'Parque das Nações'),
            ('Lisboa', 'Penha de França'),
            ('Lisboa', 'Santa Clara'),
            ('Lisboa', 'Santa Maria Maior'),
            ('Lisboa', 'Santa Maria dos Olivais'),
            ('Lisboa', 'Santo António'),
            ('Lisboa', 'São Domingos de Benfica'),
            ('Lisboa', 'São Vicente'),
            
            # Loures
            ('Loures', 'Apelação'),
            ('Loures', 'Bobadela'),
            ('Loures', 'Bucelas'),
            ('Loures', 'Camarate, Unhos e Apelação'),
            ('Loures', 'Fanhões'),
            ('Loures', 'Frielas'),
            ('Loures', 'Loures'),
            ('Loures', 'Lousa'),
            ('Loures', 'Moscavide e Portela'),
            ('Loures', 'Sacavém e Prior Velho'),
            ('Loures', 'Santa Iria de Azóia, São João da Talha e Bobadela'),
            ('Loures', 'Santo Antão do Tojal'),
            ('Loures', 'Santo António dos Cavaleiros e Frielas'),
            ('Loures', 'São Julião do Tojal'),
            
            # Lourinhã
            ('Lourinhã', 'Atalaia'),
            ('Lourinhã', 'Lourinhã e Atalaia'),
            ('Lourinhã', 'Miragaia e Marteleira'),
            ('Lourinhã', 'Moledo e Cristelo'),
            ('Lourinhã', 'Reguengo Grande'),
            ('Lourinhã', 'Santa Bárbara'),
            ('Lourinhã', 'São Lourenço'),
            ('Lourinhã', 'Vimeiro'),
            
            # Mafra
            ('Mafra', 'Azueira e Sobral da Abelheira'),
            ('Mafra', 'Carvoeira'),
            ('Mafra', 'Cheleiros'),
            ('Mafra', 'Encarnação'),
            ('Mafra', 'Ericeira'),
            ('Mafra', 'Gradil'),
            ('Mafra', 'Mafra'),
            ('Mafra', 'Malveira e São Miguel de Alcainça'),
            ('Mafra', 'Milharado'),
            ('Mafra', 'Santo Isidoro'),
            ('Mafra', 'São Miguel de Alcainça'),
            ('Mafra', 'Venda do Pinheiro e Santo Estêvão das Galés'),
            ('Mafra', 'Vila Franca do Rosário'),
            
            # Odivelas
            ('Odivelas', 'Caneças'),
            ('Odivelas', 'Famões'),
            ('Odivelas', 'Odivelas'),
            ('Odivelas', 'Olival Basto'),
            ('Odivelas', 'Pontinha e Famões'),
            ('Odivelas', 'Ramada e Caneças'),
            
            # Oeiras
            ('Oeiras', 'Algés, Linda-a-Velha e Cruz Quebrada-Dafundo'),
            ('Oeiras', 'Barcarena'),
            ('Oeiras', 'Carnaxide e Queijas'),
            ('Oeiras', 'Oeiras e São Julião da Barra, Paço de Arcos e Caxias'),
            ('Oeiras', 'Porto Salvo'),
            
            # Sintra
            ('Sintra', 'Agualva e Mira-Sintra'),
            ('Sintra', 'Algueirão-Mem Martins'),
            ('Sintra', 'Cacém e São Marcos'),
            ('Sintra', 'Casal de Cambra'),
            ('Sintra', 'Colares'),
            ('Sintra', 'Massamá e Monte Abraão'),
            ('Sintra', 'Queluz e Belas'),
            ('Sintra', 'Rio de Mouro'),
            ('Sintra', 'São João das Lampas e Terrugem'),
            ('Sintra', 'São Pedro de Penaferrim'),
            ('Sintra', 'Sintra (Santa Maria e São Miguel, São Martinho e São Pedro de Penaferrim)'),
            
            # Sobral de Monte Agraço
            ('Sobral de Monte Agraço', 'Sobral de Monte Agraço'),
            ('Sobral de Monte Agraço', 'Santo Quintino'),
            
            # Torres Vedras
            ('Torres Vedras', 'A dos Cunhados e Maceira'),
            ('Torres Vedras', 'Campelos e Outeiro da Cabeça'),
            ('Torres Vedras', 'Carvoeira e Carmões'),
            ('Torres Vedras', 'Freiria'),
            ('Torres Vedras', 'Lourinhã e Atalaia'),
            ('Torres Vedras', 'Matacães'),
            ('Torres Vedras', 'Monte Redondo e Carreira'),
            ('Torres Vedras', 'Ponte do Rol'),
            ('Torres Vedras', 'Ramalhal'),
            ('Torres Vedras', 'Runa'),
            ('Torres Vedras', 'Santa Cruz'),
            ('Torres Vedras', 'São Pedro da Cadeira'),
            ('Torres Vedras', 'São Pedro e Santiago'),
            ('Torres Vedras', 'Silveira'),
            ('Torres Vedras', 'Torres Vedras (Santa Maria, São Pedro e Matacães)'),
            ('Torres Vedras', 'Torres Vedras (Santo André e São Pedro da Cadeira)'),
            ('Torres Vedras', 'Turcifal'),
            ('Torres Vedras', 'Ventosa'),
            
            # Vila Franca de Xira
            ('Vila Franca de Xira', 'Alhandra, São João dos Montes e Calhandriz'),
            ('Vila Franca de Xira', 'Alverca do Ribatejo e Sobralinho'),
            ('Vila Franca de Xira', 'Cachoeiras'),
            ('Vila Franca de Xira', 'Castanheira do Ribatejo e Cachoeiras'),
            ('Vila Franca de Xira', 'Póvoa de Santa Iria e Forte da Casa'),
            ('Vila Franca de Xira', 'Vialonga'),
            ('Vila Franca de Xira', 'Vila Franca de Xira'),
        ]

        # Create districts
        self.stdout.write('Creating districts...')
        district_objects = {}
        for district_name in districts:
            district, created = District.objects.get_or_create(name=district_name)
            district_objects[districts.index(district_name) + 1] = district
            if created:
                self.stdout.write(f'Created district: {district_name}')
            else:
                self.stdout.write(f'District already exists: {district_name}')

        # Create counties
        self.stdout.write('Creating counties...')
        county_objects = {}
        for district_id, county_name in counties_data:
            district = district_objects[district_id]
            county, created = County.objects.get_or_create(
                name=county_name,
                district=district
            )
            county_objects[county_name] = county
            if created:
                self.stdout.write(f'Created county: {county_name} in {district.name}')
            else:
                self.stdout.write(f'County already exists: {county_name} in {district.name}')

        # Create parishes
        self.stdout.write('Creating parishes...')
        for county_name, parish_name in parishes_data:
            if county_name in county_objects:
                county = county_objects[county_name]
                parish, created = Parish.objects.get_or_create(
                    name=parish_name,
                    county=county
                )
                if created:
                    self.stdout.write(f'Created parish: {parish_name} in {county.name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated {len(districts)} districts, {len(counties_data)} counties, and {len(parishes_data)} parishes'
            )
        )
