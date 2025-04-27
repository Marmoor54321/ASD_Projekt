# Problem komiwojażera
# O projekcie  
Projekt zajmuje się badaniem i testowaniem metod rozwiązywania [problemu komiwojażera](https://pl.wikipedia.org/wiki/Problem_komiwoja%C5%BCera) w języku Python w ramach przedmiotu akademickiego Algorytmy i struktury danych.
Podczas realizacji projektu wykorzystano spis danych 1000 firm położonych w Warszawie i jej okolicach (plik Warszawa.csv).  
Projekt nie jest przeznaczony do użytku publicznego. Z tego powodu wykorzystywany w kodzie klucz API OpenRouteService jest nieaktwny.
# Funkcjonalności 
- Obliczanie najkrótszej trasy pomiędzy punktem głównym (Depot), a innymi punktami
- Wyświetlanie tras na mapie i generowanie plików html  

![image](https://github.com/user-attachments/assets/af2b5949-433b-4a8d-a63d-a48cbf615d4e)


- Obliczanie najkrótszej trasy dla N wylosowanych punktów za pomocą algorytmów przybliżonych i dokładnych. 


![image](https://github.com/user-attachments/assets/4e9f9435-5966-4f4e-8b75-9517c2feb1fe)

- Generowanie klastrów adresów  

![image](https://github.com/user-attachments/assets/7a35f244-5fdc-4dab-b113-512a40212e48)  

- Obliczanie najkrótszych tras dostawczych dla N wylosowanych adresów podzielonych na K (ilość kierowców) klastrów. Każda trasa zaczyna się w punkcie Depot  

![image](https://github.com/user-attachments/assets/a2866b94-ae0e-4563-a818-dc02bde747c7)


# Wykorzystywane algorytmy  
  Przybliżone:
  * Najbliższego sąsiada
  * Symulowane wyżarzanie
  * Grasshopper
  * 2-opt

  Dokładne:
  * Brute Force  
