import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-mealprep',
  templateUrl: './mealprep.component.html',
  styleUrls: ['./mealprep.component.css']
})
export class MealprepComponent implements OnInit {
  mealprepData: any[] = [];
  apiUrl = 'http://localhost:8000/mealprep'; // URL for your FastAPI endpoint

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.fetchMealprepData();
  }

  fetchMealprepData(): void {
    this.http.get<any[]>(this.apiUrl).subscribe(
      data => {
        this.mealprepData = data;
        console.log(this.mealprepData); // Log data for debugging purposes
      },
      error => {
        console.error('Error fetching meal prep data:', error);
      }
    );
  }
}
