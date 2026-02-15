from django.shortcuts import render
from .models import Customers
from rest_framework.response import Response
from .serializers import CustomersSerializer
from rest_framework.views import APIView
from rest_framework import status
from .services import calculate_limit

class RegisterCustomer(APIView):

    def post(self, request):
        #before we search for phone number , lets validate 
        serializer = CustomersSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data.get('phone_number')
            if Customers.objects.filter(phone_number=phone_number).exists():
                return Response({"error": "Customer already exists"}, status=status.HTTP_400_BAD_REQUEST)
            limit = calculate_limit(serializer.validated_data.get('monthly_salary'))
            serializer.save(approved_limit=limit)
            return Response({
                "message": "Customer registered successfully",
                "data": {
                    "customer_id": serializer.instance.id,
                    "first_name": serializer.validated_data.get('first_name'),
                    "last_name": serializer.validated_data.get('last_name'),
                    "age": serializer.validated_data.get('age'),
                    "phone_number": serializer.validated_data.get('phone_number'),
                    "monthly_salary": serializer.validated_data.get('monthly_salary'),
                    #approved limit is a derived data 
                    "approved_limit": limit,
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "message": "Invalid data",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
