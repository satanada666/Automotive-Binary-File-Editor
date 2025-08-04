def compare_binary_files(file1_path, file2_path, output_diff_file, output_table_file):
    with open(file1_path, 'rb') as f1, open(file2_path, 'rb') as f2:
        data1 = f1.read()
        data2 = f2.read()
        
        # Проверяем длину файлов
        if len(data1) != len(data2):
            print("Файлы имеют разную длину! Сравнение возможно только до минимальной длины.")
            min_len = min(len(data1), len(data2))
            data1 = data1[:min_len]
            data2 = data2[:min_len]
        else:
            min_len = len(data1)
        
        # Список для хранения различий
        differences = []
        
        # Сравнение побайтно и сбор различий
        for i in range(min_len):
            if data1[i] != data2[i]:
                differences.append((i, data1[i], data2[i]))
        
        # Запись первого файла (только различия второго файла)
        with open(output_diff_file, 'w') as out:
            out.write("File2_Byte differences:\n")
            formatted_output = ", ".join([f"(0x{addr:06X}, 0x{byte2:02X})" for addr, _, byte2 in differences])
            out.write(formatted_output + "\n")
        
        # Запись второго файла (таблица с Address, File1_Byte, File2_Byte)
        with open(output_table_file, 'w') as out:
            out.write("Address    File1_Byte    File2_Byte\n")
            for addr, byte1, byte2 in differences:
                out.write(f"0x{addr:06X}   0x{byte1:02X}        0x{byte2:02X}\n")
        
        print(f"Отчет сохранен в {output_diff_file} и {output_table_file}")
        print(f"Найдено различий: {len(differences)}")

# Пример использования
compare_binary_files(
    "CG100X_1_8_8_2_20250706_001801_BMW_SME_Battery_Management_Module(crash).bin",
    "CG100X_1_8_9_0_20250723_135144_BMW_SME_Battery_Management_Module(clear).bin",
    "differences.txt",
    "differences_table.txt"
)